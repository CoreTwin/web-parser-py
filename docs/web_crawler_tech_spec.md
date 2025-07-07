# Техническое задание: Система веб-краулинга и обработки данных

## 1. Анализ предварительного описания

### Сильные стороны документа:
- Хорошо продуманная микросервисная архитектура
- Грамотный выбор технологического стека
- Учет требований безопасности и масштабируемости
- Детальное описание функциональных возможностей

### Выявленные пробелы:
- Отсутствие детальной архитектуры БД
- Недостаточное описание API-контрактов
- Нет спецификации протоколов межсервисного взаимодействия
- Отсутствует план развертывания и CI/CD
- Нет описания системы мониторинга и алертинга

## 2. Детальное техническое задание

### 2.1. Архитектура системы

#### 2.1.1. Микросервисы

**API Gateway Service**
- Технологии: Go + Gin/Echo
- Функции: маршрутизация, аутентификация, rate limiting, CORS
- Порт: 8080
- Зависимости: Redis (сессии), PostgreSQL (пользователи)

**Crawler Service**
- Технологии: Python 3.11+ + FastAPI + aiohttp
- Функции: обход сайтов, извлечение ссылок, соблюдение robots.txt
- Порт: 8081
- Зависимости: Redis (очереди), PostgreSQL (метаданные)

**Parser Service**
- Технологии: Go + Colly/GoQuery
- Функции: парсинг HTML, извлечение данных, применение правил
- Порт: 8082
- Зависимости: Redis (кэш селекторов), PostgreSQL (результаты)

**File Processor Service**
- Технологии: Python + FastAPI
- Функции: скачивание файлов, конвертация, OCR
- Порт: 8083
- Зависимости: S3-совместимое хранилище, Redis (статус обработки)

**Scheduler Service**
- Технологии: Go + Cron
- Функции: планирование задач, управление очередями
- Порт: 8084
- Зависимости: Redis (очереди), PostgreSQL (расписания)

**Notification Service**
- Технологии: Node.js + Express + Socket.io
- Функции: WebSocket-соединения, уведомления
- Порт: 8085
- Зависимости: Redis (pub/sub)

**Analytics Service**
- Технологии: Python + FastAPI + Pandas
- Функции: агрегация данных, генерация отчетов
- Порт: 8086
- Зависимости: ClickHouse, PostgreSQL

#### 2.1.2. Схема базы данных

**PostgreSQL Schema:**

```sql
-- Пользователи и авторизация
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Проекты краулинга
CREATE TABLE projects (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    user_id INTEGER REFERENCES users(id),
    config JSONB NOT NULL,
    status VARCHAR(20) DEFAULT 'inactive',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Задачи краулинга
CREATE TABLE crawl_tasks (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id),
    url VARCHAR(2048) NOT NULL,
    priority INTEGER DEFAULT 0,
    depth INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'pending',
    retry_count INTEGER DEFAULT 0,
    scheduled_at TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    error_message TEXT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Результаты парсинга
CREATE TABLE parsed_data (
    id SERIAL PRIMARY KEY,
    task_id INTEGER REFERENCES crawl_tasks(id),
    url VARCHAR(2048) NOT NULL,
    title TEXT,
    content TEXT,
    extracted_data JSONB,
    file_urls TEXT[],
    links TEXT[],
    parsed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    content_hash VARCHAR(64),
    UNIQUE(url, content_hash)
);

-- Скачанные файлы
CREATE TABLE downloaded_files (
    id SERIAL PRIMARY KEY,
    task_id INTEGER REFERENCES crawl_tasks(id),
    url VARCHAR(2048) NOT NULL,
    file_path VARCHAR(500),
    file_size BIGINT,
    mime_type VARCHAR(100),
    status VARCHAR(20) DEFAULT 'pending',
    downloaded_at TIMESTAMP,
    metadata JSONB
);

-- Правила парсинга
CREATE TABLE parsing_rules (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id),
    name VARCHAR(100) NOT NULL,
    selector_type VARCHAR(20) NOT NULL, -- css, xpath, regex
    selector_value TEXT NOT NULL,
    extraction_type VARCHAR(20) NOT NULL, -- text, html, attribute
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Индексы для оптимизации
CREATE INDEX idx_crawl_tasks_status ON crawl_tasks(status);
CREATE INDEX idx_crawl_tasks_project_id ON crawl_tasks(project_id);
CREATE INDEX idx_parsed_data_url ON parsed_data(url);
CREATE INDEX idx_parsed_data_content_hash ON parsed_data(content_hash);
CREATE INDEX idx_downloaded_files_status ON downloaded_files(status);
```

#### 2.1.3. API Contracts

**Crawler API Endpoints:**

```yaml
# crawler-api.yaml
openapi: 3.0.0
info:
  title: Web Crawler API
  version: 1.0.0

paths:
  /api/v1/projects:
    get:
      summary: Получить список проектов
      responses:
        '200':
          description: Список проектов
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/Project'
    post:
      summary: Создать новый проект
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateProjectRequest'

  /api/v1/projects/{id}/start:
    post:
      summary: Запустить краулинг проекта
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: integer

  /api/v1/tasks:
    get:
      summary: Получить список задач
      parameters:
        - name: project_id
          in: query
          schema:
            type: integer
        - name: status
          in: query
          schema:
            type: string
            enum: [pending, running, completed, failed]

components:
  schemas:
    Project:
      type: object
      properties:
        id:
          type: integer
        name:
          type: string
        description:
          type: string
        config:
          type: object
        status:
          type: string
          enum: [active, inactive, paused]
        created_at:
          type: string
          format: date-time
```

### 2.2. Технические требования

#### 2.2.1. Производительность
- Обработка до 1000 URL/минуту на один воркер
- Поддержка до 50 одновременных соединений
- Время отклика API < 500ms для простых запросов
- Масштабирование до 10 воркеров без деградации

#### 2.2.2. Надежность
- Availability: 99.5% uptime
- Автоматическое восстановление после сбоев
- Graceful shutdown всех сервисов
- Откат задач при сбое

#### 2.2.3. Безопасность
- JWT-токены для аутентификации (exp: 24h)
- Rate limiting: 100 запросов/минуту на IP
- Хеширование паролей: bcrypt с cost=12
- Валидация всех входных данных
- Логирование всех операций

### 2.3. Конфигурация сервисов

#### 2.3.1. Crawler Service Configuration

```yaml
# crawler-config.yaml
crawler:
  max_concurrent_requests: 50
  delay_between_requests: 1000ms
  request_timeout: 30s
  max_retries: 3
  respect_robots_txt: true
  user_agents:
    - "Mozilla/5.0 (compatible; CrawlerBot/1.0)"
  proxy:
    enabled: false
    rotation_enabled: true
    proxies: []
  
parsing:
  max_content_size: 10MB
  allowed_content_types:
    - text/html
    - application/xhtml+xml
  extract_links: true
  extract_images: true
  extract_documents: true
  
storage:
  max_file_size: 100MB
  allowed_extensions:
    - .pdf
    - .doc
    - .docx
    - .txt
    - .jpg
    - .png
```

#### 2.3.2. Docker Compose Configuration

```yaml
version: '3.8'

services:
  api-gateway:
    build:
      context: ./api-gateway
      dockerfile: Dockerfile
    ports:
      - "8080:8080"
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/crawler_db
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - postgres
      - redis

  crawler-service:
    build:
      context: ./crawler-service
      dockerfile: Dockerfile
    ports:
      - "8081:8081"
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/crawler_db
      - REDIS_URL=redis://redis:6379/1
    depends_on:
      - postgres
      - redis
    deploy:
      replicas: 3

  parser-service:
    build:
      context: ./parser-service
      dockerfile: Dockerfile
    ports:
      - "8082:8082"
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/crawler_db
      - REDIS_URL=redis://redis:6379/2
    depends_on:
      - postgres
      - redis
    deploy:
      replicas: 2

  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=crawler_db
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  clickhouse:
    image: clickhouse/clickhouse-server:latest
    ports:
      - "8123:8123"
      - "9000:9000"
    volumes:
      - clickhouse_data:/var/lib/clickhouse

volumes:
  postgres_data:
  redis_data:
  clickhouse_data:
```

### 2.4. Мониторинг и логирование

#### 2.4.1. Prometheus Metrics

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'crawler-services'
    static_configs:
      - targets: ['api-gateway:8080', 'crawler-service:8081', 'parser-service:8082']
    metrics_path: '/metrics'
    scrape_interval: 10s

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']
```

#### 2.4.2. Structured Logging

```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "INFO",
  "service": "crawler-service",
  "message": "Started crawling task",
  "context": {
    "task_id": 12345,
    "project_id": 67,
    "url": "https://example.com",
    "depth": 2
  },
  "trace_id": "abc123def456"
}
```

### 2.5. CI/CD Pipeline

#### 2.5.1. GitHub Actions Workflow

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Go
        uses: actions/setup-go@v3
        with:
          go-version: 1.21
      - name: Run tests
        run: |
          go test ./... -v -coverprofile=coverage.out
          go tool cover -html=coverage.out -o coverage.html
      - name: Upload coverage
        uses: codecov/codecov-action@v3

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build Docker images
        run: |
          docker build -t crawler-api-gateway ./api-gateway
          docker build -t crawler-service ./crawler-service
          docker build -t parser-service ./parser-service
      - name: Push to registry
        run: |
          echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
          docker push crawler-api-gateway
          docker push crawler-service
          docker push parser-service

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - name: Deploy to staging
        run: |
          kubectl set image deployment/api-gateway api-gateway=crawler-api-gateway:latest
          kubectl set image deployment/crawler-service crawler-service=crawler-service:latest
```

## 3. План разработки

### 3.1. Этап 1: Фундамент (2 недели)

**Задачи:**
1. Настройка инфраструктуры разработки
   - Создание Git-репозитория с структурой монорепо
   - Настройка Docker-окружения
   - Создание схемы БД и миграций
   - Настройка CI/CD pipeline

2. Базовая авторизация
   - Реализация JWT-аутентификации
   - API регистрации/входа
   - Middleware для проверки токенов

**Критерии готовности:**
- Запускается Docker Compose с базовыми сервисами
- Работает регистрация и авторизация
- Проходят unit-тесты
- Настроен линтинг и форматирование кода

### 3.2. Этап 2: Ядро краулинга (3 недели)

**Задачи:**
1. Crawler Service
   - Базовый HTTP-клиент с retry-логикой
   - Обработка robots.txt
   - Извлечение ссылок из HTML
   - Очередь задач через Redis

2. Parser Service
   - HTML-парсинг с BeautifulSoup/Colly
   - Применение CSS/XPath селекторов
   - Сохранение результатов в БД

3. API Gateway
   - Маршрутизация запросов
   - Rate limiting
   - Базовая документация API

**Критерии готовности:**
- Можно создать проект краулинга
- Работает обход простых сайтов
- Сохраняются результаты парсинга
- Есть логи и базовые метрики

### 3.3. Этап 3: Веб-интерфейс (2 недели)

**Задачи:**
1. React-приложение
   - Настройка Vite + TypeScript
   - Компоненты для управления проектами
   - Формы создания и настройки задач
   - Таблицы с результатами

2. Интеграция с API
   - React Query для запросов
   - Zustand для состояния
   - WebSocket для real-time обновлений

**Критерии готовности:**
- Работает веб-интерфейс
- Можно создавать и запускать проекты
- Отображаются результаты в реальном времени
- Адаптивный дизайн для мобильных устройств

### 3.4. Этап 4: Расширенные возможности (3 недели)

**Задачи:**
1. File Processor Service
   - Скачивание файлов
   - Конвертация форматов
   - OCR для изображений

2. Scheduler Service
   - Планирование задач по расписанию
   - Управление приоритетами
   - Автоматический перезапуск неудачных задач

3. Analytics Service
   - Агрегация статистики
   - Генерация отчетов
   - Экспорт данных в различных форматах

**Критерии готовности:**
- Работает скачивание файлов
- Функционирует планировщик задач
- Доступны детальные отчеты
- Все сервисы интегрированы

### 3.5. Этап 5: Оптимизация и безопасность (2 недели)

**Задачи:**
1. Производительность
   - Оптимизация запросов к БД
   - Кэширование часто используемых данных
   - Профилирование и устранение узких мест

2. Безопасность
   - Аудит безопасности кода
   - Защита от SQL-инъекций
   - Валидация входных данных
   - Настройка HTTPS

3. Мониторинг
   - Prometheus + Grafana
   - Алерты на критические события
   - Dashboards для мониторинга

**Критерии готовности:**
- Система выдерживает нагрузочные тесты
- Проходит аудит безопасности
- Работает мониторинг и алерты
- Документация готова к продакшену

## 4. Дальнейшее развитие и улучшения

### 4.1. Краткосрочные улучшения (3-6 месяцев)

#### 4.1.1. Интеллектуальный краулинг
- **Machine Learning для приоритизации:** Обучение модели для определения важности страниц на основе исторических данных
- **Автоматическое обнаружение селекторов:** Использование computer vision для автоматического определения структуры страниц
- **Дедупликация контента:** Алгоритмы для выявления и исключения дублированного контента

#### 4.1.2. Продвинутая обработка данных
- **NLP-анализ:** Извлечение сущностей, тональности, ключевых слов
- **Автоматическая категоризация:** Классификация контента по темам
- **Семантический поиск:** Поиск по смыслу, а не только по ключевым словам

#### 4.1.3. Расширенные источники данных
- **API-интеграции:** Подключение к популярным API (Twitter, Reddit, RSS)
- **Социальные сети:** Специализированные парсеры для соцсетей
- **Документы:** Расширенная поддержка форматов (Excel, PowerPoint, архивы)

### 4.2. Среднесрочные улучшения (6-12 месяцев)

#### 4.2.1. Масштабируемость
- **Kubernetes-нативная архитектура:** Полный переход на K8s с автоскалированием
- **Distributed crawling:** Распределенное выполнение задач между множеством узлов
- **Микросервисы 2.0:** Разбиение на более мелкие специализированные сервисы

#### 4.2.2. Продвинутая аналитика
- **Граф знаний:** Построение семантических связей между данными
- **Временные ряды:** Анализ изменений данных во времени
- **Предиктивная аналитика:** Прогнозирование трендов и изменений

#### 4.2.3. Пользовательский опыт
- **Визуальный редактор правил:** Drag-and-drop интерфейс для создания правил парсинга
- **Шаблоны проектов:** Готовые конфигурации для популярных типов сайтов
- **Коллаборативные возможности:** Совместная работа над проектами

### 4.3. Долгосрочные улучшения (1-2 года)

#### 4.3.1. Искусственный интеллект
- **Автономный краулинг:** ИИ-агент, способный самостоятельно определять стратегию обхода
- **Генеративный ИИ:** Создание синтетических данных для тестирования
- **Адаптивные правила:** Автоматическое обновление правил парсинга при изменении структуры сайтов

#### 4.3.2. Экосистема
- **Marketplace плагинов:** Магазин расширений от сообщества разработчиков
- **API для третьих лиц:** Открытые API для интеграции с внешними системами
- **Белый лейбл:** Возможность ребрендинга для корпоративных клиентов

#### 4.3.3. Специализированные модули
- **Финансовые данные:** Специализированные парсеры для биржевых данных
- **Научные публикации:** Интеграция с академическими базами данных
- **Государственные данные:** Специальные модули для работы с открытыми данными

### 4.4. Технические инновации

#### 4.4.1. Новые технологии
- **WebAssembly:** Высокопроизводительные парсеры на Rust/C++
- **GraphQL:** Более гибкие API для сложных запросов
- **Blockchain:** Система репутации для источников данных

#### 4.4.2. Архитектурные решения
- **Event-driven architecture:** Полностью событийная архитектура
- **Serverless components:** Использование AWS Lambda/Google Cloud Functions
- **Edge computing:** Распределенные узлы краулинга по всему миру

#### 4.4.3. Безопасность следующего поколения
- **Zero-trust architecture:** Полная верификация всех запросов
- **Homomorphic encryption:** Обработка зашифрованных данных
- **Privacy-preserving crawling:** Анонимизация данных на лету

## 5. Риски и митигация

### 5.1. Технические риски
- **Блокировка IP:** Использование proxy-пулов и rotation
- **Изменение структуры сайтов:** Автоматическое обнаружение изменений
- **Производительность БД:** Шардинг и оптимизация индексов

### 5.2. Правовые риски
- **Нарушение ToS:** Строгое соблюдение robots.txt и rate limiting
- **Авторские права:** Система фильтрации контента
- **GDPR compliance:** Механизмы удаления персональных данных

### 5.3. Операционные риски
- **Перегрузка команды:** Поэтапное развитие с четкими milestone
- **Технический долг:** Регулярные рефакторинги и code review
- **Vendor lock-in:** Использование open-source решений где возможно

## 6. Заключение

Предложенная система веб-краулинга представляет собой масштабируемое, безопасное и расширяемое решение для сбора и обработки веб-данных. Поэтапный план разработки позволяет быстро получить работающий MVP и постепенно наращивать функциональность.

Ключевые преимущества архитектуры:
- **Модульность:** Независимые микросервисы
- **Масштабируемость:** Горизонтальное масштабирование
- **Надежность:** Обработка ошибок и восстановление
- **Безопасность:** Многоуровневая защита данных
- **Гибкость:** Возможность адаптации под различные задачи

Ключевые дополнения:
1. Детальная архитектура

Точная спецификация каждого микросервиса с портами и зависимостями
Полная схема PostgreSQL с индексами и связями
API-контракты в формате OpenAPI/Swagger
Docker Compose конфигурация для локальной разработки

2. Технические требования

Конкретные метрики производительности (1000 URL/мин, 99.5% uptime)
Требования к безопасности (JWT с 24h TTL, bcrypt cost=12)
Детальная конфигурация сервисов в YAML

3. Мониторинг и операции

Prometheus метрики и Grafana дашборды
Структурированное логирование в JSON
CI/CD pipeline с GitHub Actions
Kubernetes deployment стратегии

4. Пошаговый план разработки

5 этапов по 2-3 недели каждый
Четкие критерии готовности для каждого этапа
Приоритизация функций от MVP к продвинутым возможностям

5. Долгосрочная стратегия развития

Краткосрочные улучшения (ML, NLP, автоматизация)
Среднесрочные (Kubernetes, граф знаний, коллаборация)
Долгосрочные (ИИ-агенты, экосистема плагинов, blockchain)

6. Управление рисками

Технические риски и их митигация
Правовые аспекты (GDPR, ToS, авторские права)
Операционные риски разработки
