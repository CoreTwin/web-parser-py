# Детальный план проекта системы веб-краулинга с автодокументацией

## 1. Обновленная архитектура с интеграцией Docusaurus

### 1.1. Новая структура проекта

```
web-crawler-system/
├── docs/                           # Docusaurus документация
│   ├── docusaurus.config.js
│   ├── sidebars.js
│   ├── src/
│   │   ├── components/
│   │   ├── css/
│   │   └── pages/
│   ├── docs/
│   │   ├── getting-started/
│   │   ├── api-reference/
│   │   ├── architecture/
│   │   ├── deployment/
│   │   └── examples/
│   ├── blog/
│   └── static/
├── services/
│   ├── api-gateway/
│   ├── crawler-service/
│   ├── parser-service/
│   ├── file-processor/
│   ├── scheduler/
│   ├── notification/
│   ├── analytics/
│   └── docs-service/              # Новый сервис документации
├── web-app/                       # React фронтенд
├── infrastructure/
│   ├── docker/
│   ├── kubernetes/
│   ├── terraform/
│   └── monitoring/
├── shared/
│   ├── schemas/
│   ├── types/
│   └── utils/
└── scripts/
    ├── deployment/
    ├── migrations/
    └── automation/
```

### 1.2. Docs Service - Сервис документации

**Технологии:** Node.js + Express + Docusaurus
**Порт:** 8087
**Функции:**
- Автогенерация API-документации из OpenAPI схем
- Интеграция с Swagger/OpenAPI
- Автоматическое обновление документации при изменениях
- Версионирование документации
- Поиск по документации

```javascript
// services/docs-service/src/app.js
const express = require('express');
const swaggerJsdoc = require('swagger-jsdoc');
const swaggerUi = require('swagger-ui-express');
const { exec } = require('child_process');
const fs = require('fs');
const path = require('path');

const app = express();

// Swagger configuration
const swaggerOptions = {
  definition: {
    openapi: '3.0.0',
    info: {
      title: 'Web Crawler API',
      version: '1.0.0',
      description: 'Comprehensive API for web crawling system'
    },
    servers: [
      {
        url: 'http://localhost:8080',
        description: 'Development server'
      }
    ]
  },
  apis: ['../*/src/routes/*.js', '../*/src/handlers/*.go']
};

const swaggerSpec = swaggerJsdoc(swaggerOptions);

// Auto-generate API docs
app.get('/api-docs/swagger.json', (req, res) => {
  res.setHeader('Content-Type', 'application/json');
  res.send(swaggerSpec);
});

// Serve Swagger UI
app.use('/api-docs', swaggerUi.serve, swaggerUi.setup(swaggerSpec));

// Auto-update documentation
app.post('/docs/update', async (req, res) => {
  try {
    // Regenerate OpenAPI specs
    await generateOpenAPISpecs();
    
    // Rebuild Docusaurus
    exec('cd ../docs && npm run build', (error, stdout, stderr) => {
      if (error) {
        console.error(`Error building docs: ${error}`);
        return res.status(500).json({ error: 'Failed to build documentation' });
      }
      res.json({ message: 'Documentation updated successfully' });
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

async function generateOpenAPISpecs() {
  // Auto-generate OpenAPI specs from service endpoints
  const services = ['api-gateway', 'crawler-service', 'parser-service'];
  
  for (const service of services) {
    const specPath = path.join(__dirname, `../../${service}/openapi.yaml`);
    if (fs.existsSync(specPath)) {
      const spec = fs.readFileSync(specPath, 'utf8');
      const outputPath = path.join(__dirname, '../docs/docs/api-reference/', `${service}.md`);
      
      // Convert OpenAPI to Markdown
      const markdown = await convertOpenAPIToMarkdown(spec);
      fs.writeFileSync(outputPath, markdown);
    }
  }
}

app.listen(8087, () => {
  console.log('Documentation service running on port 8087');
});
```

### 1.3. Docusaurus конфигурация

```javascript
// docs/docusaurus.config.js
const config = {
  title: 'Web Crawler System',
  tagline: 'Comprehensive web crawling and data processing platform',
  url: 'https://crawler-docs.yourcompany.com',
  baseUrl: '/',
  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',
  favicon: 'img/favicon.ico',
  organizationName: 'yourcompany',
  projectName: 'web-crawler-system',

  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: require.resolve('./sidebars.js'),
          editUrl: 'https://github.com/yourcompany/web-crawler-system/tree/main/docs/',
          showLastUpdateTime: true,
          showLastUpdateAuthor: true,
        },
        blog: {
          showReadingTime: true,
          editUrl: 'https://github.com/yourcompany/web-crawler-system/tree/main/docs/',
        },
        theme: {
          customCss: require.resolve('./src/css/custom.css'),
        },
      },
    ],
  ],

  themeConfig: {
    navbar: {
      title: 'Web Crawler',
      logo: {
        alt: 'Web Crawler Logo',
        src: 'img/logo.svg',
      },
      items: [
        {
          type: 'doc',
          docId: 'getting-started/installation',
          position: 'left',
          label: 'Docs',
        },
        {
          to: 'api-reference',
          label: 'API Reference',
          position: 'left',
        },
        {
          to: '/blog',
          label: 'Blog',
          position: 'left'
        },
        {
          href: 'https://github.com/yourcompany/web-crawler-system',
          label: 'GitHub',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Docs',
          items: [
            {
              label: 'Getting Started',
              to: '/docs/getting-started/installation',
            },
            {
              label: 'API Reference',
              to: '/docs/api-reference',
            },
          ],
        },
        {
          title: 'Community',
          items: [
            {
              label: 'Discord',
              href: 'https://discord.gg/yourserver',
            },
            {
              label: 'Twitter',
              href: 'https://twitter.com/yourcompany',
            },
          ],
        },
      ],
      copyright: `Copyright © ${new Date().getFullYear()} Your Company. Built with Docusaurus.`,
    },
    prism: {
      theme: require('prism-react-renderer/themes/github'),
      darkTheme: require('prism-react-renderer/themes/dracula'),
      additionalLanguages: ['go', 'yaml', 'docker', 'sql'],
    },
    algolia: {
      apiKey: 'your-api-key',
      indexName: 'web-crawler-docs',
      appId: 'your-app-id',
    },
  },

  plugins: [
    [
      '@docusaurus/plugin-content-docs',
      {
        id: 'api-reference',
        path: 'api-reference',
        routeBasePath: 'api-reference',
        sidebarPath: require.resolve('./sidebars-api.js'),
      },
    ],
    [
      'docusaurus-plugin-openapi-docs',
      {
        id: 'openapi',
        docsPluginId: 'api-reference',
        config: {
          api: {
            specPath: '../services/api-gateway/openapi.yaml',
            outputDir: 'api-reference',
            sidebarOptions: {
              groupPathsBy: 'tag',
            },
          },
        },
      },
    ],
  ],
};

module.exports = config;
```

### 1.4. Автоматизация документации

```yaml
# .github/workflows/docs-update.yml
name: Update Documentation

on:
  push:
    branches: [main, develop]
    paths:
      - 'services/*/openapi.yaml'
      - 'services/*/src/**/*.go'
      - 'services/*/src/**/*.py'
      - 'docs/**/*'

jobs:
  update-docs:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: 18

      - name: Install dependencies
        run: |
          cd docs
          npm ci

      - name: Generate API docs
        run: |
          cd services/docs-service
          npm install
          npm run generate-specs

      - name: Build documentation
        run: |
          cd docs
          npm run build

      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./docs/build

      - name: Update service documentation
        run: |
          curl -X POST http://localhost:8087/docs/update
```

## 2. Детальный план разработки (обновленный)

### 2.1. Этап 0: Подготовка инфраструктуры документации (1 неделя)

**Задачи:**
1. **Настройка Docusaurus**
   - Инициализация проекта документации
   - Конфигурация тем и плагинов
   - Настройка поиска через Algolia
   - Интеграция с GitHub Pages

2. **Создание базовой структуры документации**
   - Архитектурная документация
   - Руководство по установке
   - Шаблоны для API-документации
   - Примеры использования

3. **Автоматизация процесса документирования**
   - Настройка auto-generation из OpenAPI
   - CI/CD для автоматического обновления
   - Интеграция с системой версионирования

**Критерии готовности:**
- Работает сайт документации
- Автоматически обновляется при изменениях
- Настроен поиск по документации
- Есть базовые разделы документации

### 2.2. Этап 1: Фундамент системы (2 недели)

**Задачи:**
1. **Инфраструктура разработки**
   - Создание монорепозитория с правильной структурой
   - Настройка Docker Compose для локальной разработки
   - Создание схемы БД с полными миграциями
   - Настройка GitHub Actions CI/CD

2. **Базовая авторизация и безопасность**
   - JWT-аутентификация с refresh tokens
   - Middleware для проверки токенов
   - Rate limiting с Redis
   - Базовая система ролей

3. **Микросервисная архитектура**
   - API Gateway с маршрутизацией
   - Базовые сервисы (заглушки)
   - Inter-service communication
   - Health check endpoints

**Детальная реализация:**

```go
// services/api-gateway/internal/middleware/auth.go
package middleware

import (
    "context"
    "net/http"
    "strings"
    "time"

    "github.com/gin-gonic/gin"
    "github.com/golang-jwt/jwt/v5"
    "github.com/redis/go-redis/v9"
)

type AuthMiddleware struct {
    jwtSecret   string
    redisClient *redis.Client
}

func NewAuthMiddleware(jwtSecret string, redisClient *redis.Client) *AuthMiddleware {
    return &AuthMiddleware{
        jwtSecret:   jwtSecret,
        redisClient: redisClient,
    }
}

func (a *AuthMiddleware) RequireAuth() gin.HandlerFunc {
    return func(c *gin.Context) {
        authHeader := c.GetHeader("Authorization")
        if authHeader == "" {
            c.JSON(http.StatusUnauthorized, gin.H{"error": "Authorization header required"})
            c.Abort()
            return
        }

        tokenString := strings.TrimPrefix(authHeader, "Bearer ")
        if tokenString == authHeader {
            c.JSON(http.StatusUnauthorized, gin.H{"error": "Invalid authorization header format"})
            c.Abort()
            return
        }

        // Verify JWT token
        claims := &jwt.RegisteredClaims{}
        token, err := jwt.ParseWithClaims(tokenString, claims, func(token *jwt.Token) (interface{}, error) {
            return []byte(a.jwtSecret), nil
        })

        if err != nil || !token.Valid {
            c.JSON(http.StatusUnauthorized, gin.H{"error": "Invalid token"})
            c.Abort()
            return
        }

        // Check if token is blacklisted
        ctx := context.Background()
        blacklisted, err := a.redisClient.Get(ctx, "blacklist:"+tokenString).Result()
        if err == nil && blacklisted == "true" {
            c.JSON(http.StatusUnauthorized, gin.H{"error": "Token has been revoked"})
            c.Abort()
            return
        }

        // Add user info to context
        c.Set("user_id", claims.Subject)
        c.Set("token", tokenString)
        c.Next()
    }
}

func (a *AuthMiddleware) RateLimiter(requestsPerMinute int) gin.HandlerFunc {
    return func(c *gin.Context) {
        clientIP := c.ClientIP()
        key := "rate_limit:" + clientIP

        ctx := context.Background()
        current, err := a.redisClient.Get(ctx, key).Int()
        if err == nil && current >= requestsPerMinute {
            c.JSON(http.StatusTooManyRequests, gin.H{
                "error": "Rate limit exceeded",
                "retry_after": 60,
            })
            c.Abort()
            return
        }

        // Increment counter
        pipe := a.redisClient.Pipeline()
        pipe.Incr(ctx, key)
        pipe.Expire(ctx, key, time.Minute)
        pipe.Exec(ctx)

        c.Next()
    }
}
```

**Критерии готовности:**
- Запускается полная Docker-среда
- Работает JWT-аутентификация с refresh tokens
- Настроен rate limiting
- Все сервисы регистрируются в service discovery
- Проходят unit и integration тесты
- Документация автоматически обновляется

### 2.3. Этап 2: Ядро краулинга (3 недели)

**Задачи:**
1. **Crawler Service (продвинутая реализация)**
   - Асинхронный HTTP-клиент с connection pooling
   - Intelligent retry с exponential backoff
   - Robots.txt parsing и caching
   - URL normalization и deduplication
   - Distributed queue через Redis Streams

2. **Parser Service**
   - Pluggable парсеры (CSS, XPath, Regex)
   - Content extraction с ML-алгоритмами
   - Structured data detection (JSON-LD, Microdata)
   - Content similarity detection

3. **Advanced URL Management**
   - URL fingerprinting
   - Sitemap parsing
   - Link discovery и prioritization
   - Crawl budget management

**Детальная реализация Crawler Service:**

```python
# services/crawler-service/src/crawler/core.py
import asyncio
import aiohttp
import aioredis
from typing import List, Dict, Optional, AsyncGenerator
from urllib.robotparser import RobotFileParser
from urllib.parse import urljoin, urlparse
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
import hashlib

@dataclass
class CrawlTask:
    url: str
    project_id: int
    depth: int
    priority: int
    headers: Dict[str, str]
    created_at: datetime
    retry_count: int = 0
    
class AdvancedCrawler:
    def __init__(self, 
                 redis_client: aioredis.Redis,
                 max_concurrent: int = 50,
                 delay_between_requests: float = 1.0):
        self.redis = redis_client
        self.max_concurrent = max_concurrent
        self.delay_between_requests = delay_between_requests
        self.session: Optional[aiohttp.ClientSession] = None
        self.robots_cache: Dict[str, RobotFileParser] = {}
        self.last_request_time: Dict[str, datetime] = {}
        self.semaphore = asyncio.Semaphore(max_concurrent)
        
    async def start(self):
        """Initialize crawler with optimized session"""
        connector = aiohttp.TCPConnector(
            limit=100,
            limit_per_host=10,
            ttl_dns_cache=300,
            use_dns_cache=True,
            keepalive_timeout=30
        )
        
        timeout = aiohttp.ClientTimeout(
            total=30,
            connect=10,
            sock_read=20
        )
        
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={
                'User-Agent': 'CrawlerBot/1.0 (+https://yourcompany.com/bot)'
            }
        )
        
    async def stop(self):
        """Graceful shutdown"""
        if self.session:
            await self.session.close()
            
    async def crawl_url(self, task: CrawlTask) -> Optional[Dict]:
        """Crawl single URL with all checks and rate limiting"""
        async with self.semaphore:
            try:
                # Check robots.txt
                if not await self._is_allowed_by_robots(task.url):
                    logging.info(f"Blocked by robots.txt: {task.url}")
                    return None
                
                # Rate limiting
                await self._apply_rate_limit(task.url)
                
                # Perform request
                response_data = await self._fetch_url(task)
                
                if response_data:
                    # Extract links for next crawl
                    links = await self._extract_links(response_data['content'], task.url)
                    response_data['links'] = links
                    
                    # Store in Redis for parser service
                    await self._store_crawl_result(task, response_data)
                    
                return response_data
                
            except Exception as e:
                logging.error(f"Error crawling {task.url}: {e}")
                await self._handle_crawl_error(task, e)
                return None
                
    async def _fetch_url(self, task: CrawlTask) -> Optional[Dict]:
        """Fetch URL with retry logic"""
        for attempt in range(3):
            try:
                async with self.session.get(
                    task.url,
                    headers=task.headers,
                    allow_redirects=True
                ) as response:
                    
                    if response.status == 200:
                        content = await response.text()
                        return {
                            'url': str(response.url),
                            'status_code': response.status,
                            'headers': dict(response.headers),
                            'content': content,
                            'content_type': response.content_type,
                            'encoding': response.charset or 'utf-8',
                            'size': len(content),
                            'crawled_at': datetime.utcnow().isoformat()
                        }
                    else:
                        logging.warning(f"HTTP {response.status} for {task.url}")
                        
            except asyncio.TimeoutError:
                logging.warning(f"Timeout for {task.url} (attempt {attempt + 1})")
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
                
            except Exception as e:
                logging.error(f"Request error for {task.url}: {e}")
                await asyncio.sleep(2 ** attempt)
                
        return None
        
    async def _is_allowed_by_robots(self, url: str) -> bool:
        """Check robots.txt permission with caching"""
        parsed_url = urlparse(url)
        robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
        
        if robots_url not in self.robots_cache:
            try:
                rp = RobotFileParser()
                rp.set_url(robots_url)
                rp.read()
                self.robots_cache[robots_url] = rp
            except Exception:
                # If robots.txt is not accessible, assume allowed
                return True
                
        return self.robots_cache[robots_url].can_fetch('*', url)
        
    async def _apply_rate_limit(self, url: str):
        """Apply rate limiting per domain"""
        domain = urlparse(url).netloc
        
        if domain in self.last_request_time:
            time_since_last = datetime.now() - self.last_request_time[domain]
            if time_since_last.total_seconds() < self.delay_between_requests:
                sleep_time = self.delay_between_requests - time_since_last.total_seconds()
                await asyncio.sleep(sleep_time)
                
        self.last_request_time[domain] = datetime.now()
        
    async def _extract_links(self, content: str, base_url: str) -> List[str]:
        """Extract and normalize links from HTML content"""
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(content, 'html.parser')
        links = []
        
        for tag in soup.find_all(['a', 'link']):
            href = tag.get('href')
            if href:
                absolute_url = urljoin(base_url, href)
                # Normalize and validate URL
                normalized = self._normalize_url(absolute_url)
                if normalized and self._is_valid_url(normalized):
                    links.append(normalized)
                    
        return list(set(links))  # Remove duplicates
        
    def _normalize_url(self, url: str) -> str:
        """Normalize URL for consistent handling"""
        # Remove fragment
        url = url.split('#')[0]
        # Remove common tracking parameters
        # Add more normalization logic as needed
        return url
        
    def _is_valid_url(self, url: str) -> bool:
        """Validate URL format and scheme"""
        try:
            parsed = urlparse(url)
            return parsed.scheme in ['http', 'https'] and parsed.netloc
        except:
            return False
            
    async def _store_crawl_result(self, task: CrawlTask, result: Dict):
        """Store crawl result in Redis for parser service"""
        key = f"crawl_result:{task.project_id}:{hashlib.md5(task.url.encode()).hexdigest()}"
        await self.redis.setex(key, 3600, json.dumps(result))  # TTL: 1 hour
        
        # Add to processing queue
        await self.redis.lpush(f"parse_queue:{task.project_id}", key)
```

**Критерии готовности:**
- Стабильно работает обход простых и сложных сайтов
- Соблюдается robots.txt и rate limiting
- Качественно извлекаются ссылки и контент
- Есть retry-логика и error handling
- Работает distributed crawling через Redis
- Логи структурированы и информативны

### 2.4. Этап 3: Интеллектуальный парсинг (2 недели)

**Задачи:**
1. **Smart Content Extraction**
   - Автоматическое определение основного контента
   - Очистка от рекламы и навигации
   - Извлечение метаданных
   - Определение языка контента

2. **Structured Data Processing**
   - JSON-LD extraction
   - Microdata parsing
   - Schema.org recognition
   - Custom field extraction

3. **Advanced Parser Features**
   - Content similarity detection
   - Automatic template detection
   - Multi-language support
   - PDF/DOC content extraction

**Детальная реализация Parser Service:**

```go
// services/parser-service/internal/parser/smart_extractor.go
package parser

import (
    "context"
    "fmt"
    "strings"
    "regexp"
    "net/url"
    
    "github.com/PuerkitoBio/goquery"
    "github.com/abadojack/whatlanggo"
    "go.uber.org/zap"
)

type SmartExtractor struct {
    logger *zap.Logger
    config *Config
}

type ExtractionResult struct {
    Title           string            `json:"title"`
    MainContent     string            `json:"main_content"`
    Summary         string            `json:"summary"`
    Language        string            `json:"language"`
    Keywords        []string          `json:"keywords"`
    Metadata        map[string]string `json:"metadata"`
    StructuredData  []interface{}     `json:"structured_data"`
    Images          []Image           `json:"images"`
    Links           []Link            `json:"links"`
    ContentScore    float64           `json:"content_score"`
}

type Image struct {
    URL    string `json:"url"`
    Alt    string `json:"alt"`
    Title  string `json:"title"`
    Width  int    `json:"width"`
    Height int    `json:"height"`
}

type Link struct {
    URL      string `json:"url"`
    Text     string `json:"text"`
    Rel      string `json:"rel"`
    Internal bool   `json:"internal"`
}

func NewSmartExtractor(logger *zap.Logger, config *Config) *SmartExtractor {
    return &SmartExtractor{
        logger: logger,
        config: config,
    }
}

func (e *SmartExtractor) Extract(ctx context.Context, html string, pageURL string) (*ExtractionResult, error) {
    doc, err := goquery.NewDocumentFromReader(strings.NewReader(html))
    if err != nil {
        return nil, fmt.Errorf("failed to parse HTML: %w", err)
    }

    result := &ExtractionResult{
        Metadata: make(map[string]string),
    }

    // Extract title
    result.Title = e.extractTitle(doc)

    // Extract main content using multiple strategies
    result.MainContent = e.extractMainContent(doc)

    // Detect language
    result.Language = e.detectLanguage(result.MainContent)

    // Extract metadata
    result.Metadata = e.extractMetadata(doc)

    // Extract structured data
    result.StructuredData = e.extractStructuredData(doc)

    // Extract images
    result.Images = e.extractImages(doc, pageURL)

    // Extract links
    result.Links = e.extractLinks(doc, pageURL)

    // Generate summary
    result.Summary = e.generateSummary(result.MainContent)

    // Extract keywords
    result.Keywords = e.extractKeywords(result.MainContent)

    // Calculate content score
    result.ContentScore = e.calculateContentScore(result)

    return result, nil
}

func (e *SmartExtractor) extractTitle(doc *goquery.Document) string {
    // Try multiple strategies for title extraction
    strategies := []func(*goquery.Document) string{
        func(d *goquery.Document) string { return d.Find("title").First().Text() },
        func(d *goquery.Document) string { return d.Find("h1").First().Text() },
        func(d *goquery.Document) string { return d.Find("meta[property='og:title']").AttrOr("content", "") },
        func(d *goquery.Document) string { return d.Find("meta[name='twitter:title']").AttrOr("content", "") },
    }

    for _, strategy := range strategies {
        if title := strings.TrimSpace(strategy(doc)); title != "" {
            return title
        }
    }

    return ""
}

func (e *SmartExtractor) extractMainContent(doc *goquery.Document) string {
    // Content extraction strategies in order of preference
    strategies := []struct {
        name     string
        selector string
        score    int
    }{
        {"article", "article", 10},
        {"main", "main", 9},
        {"content-id", "#content, #main, #article", 8},
        {"content-class", ".content, .main, .article, .post", 7},
        {"semantic", "section, .entry-content", 6},
    }

    var bestContent string
    var bestScore int

    for _, strategy := range strategies {
        content := doc.Find(strategy.selector).First()
        if content.Length() > 0 {
            text := e.cleanText(content.Text())
            if len(text) > 100 { // Minimum content length
                score := strategy.score + e.calculateTextScore(text)
                if score > bestScore {
                    bestScore = score
                    bestContent = text
                }
            }
        }
    }

    // Fallback to body content if no specific content found
    if bestContent == "" {
        bestContent = e.extractBodyContent(doc)
    }

    return bestContent
}

func (e *SmartExtractor) extractBodyContent(doc *goquery.Document) string {
    // Remove unwanted elements
    doc.Find("script, style, nav, header, footer, aside, .sidebar, .navigation, .menu, .ads, .advertisement").Remove()

    // Extract text from body
    body := doc.Find("body").First()
    return e.cleanText(body.Text())
}

func (e *SmartExtractor) detectLangu // продолжить разрабатывать...




```

### 2.6. Этап 6: Уведомления и обратная связь (1.5 недели)

**Задачи:**

1. **Notification Service (WebSocket + Email):**

   * Реализация WebSocket-уведомлений об изменении статуса задач
   * Подписка клиентов на обновления (по проектам или пользователям)
   * Интеграция с Redis Pub/Sub для доставки событий от внутренних сервисов

2. **Поддержка Email-уведомлений:**

   * Конфигурация SMTP (через настройки)
   * Отправка email при ошибках или завершении задач

3. **Интеграция с веб-интерфейсом:**

   * Подключение WebSocket в React-приложении
   * Показ уведомлений в UI (toast/snackbar)

**Критерии готовности:**

* Поддержка real-time уведомлений через WebSocket
* Email-уведомления работают через SMTP
* Веб-интерфейс отображает уведомления корректно

---

### 2.7. Этап 7: Документооборот и файловая обработка (1.5 недели)

**Задачи:**

1. **File Processor Service:**

   * Асинхронная загрузка и валидация файлов (PDF, DOCX, изображения)
   * Распознавание текста (OCR) с использованием Tesseract или аналогов
   * Извлечение метаданных: название, автор, размер, структура

2. **Обработка и хранение:**

   * Хранение в S3-совместимом хранилище
   * Запись информации о файлах в БД

3. **Интерфейс загрузки и просмотра:**

   * UI-компоненты для загрузки/просмотра файлов
   * Интеграция с результатами задач

**Критерии готовности:**

* Поддерживается загрузка и извлечение файлов из HTML
* Файлы обрабатываются и сохраняются
* Метаданные извлекаются и доступны через API

---

### 2.8. Этап 8: Расширенная аналитика и отчётность (1.5 недели)

**Задачи:**

1. **Analytics Service:**

   * Агрегация по задачам, проектам, типам контента
   * Вычисление производительности (время обхода, ошибки, размер контента)
   * Экспорт в CSV/JSON

2. **Интерфейс аналитики:**

   * Графики и фильтры (D3.js или Recharts)
   * Компоненты статистики: таймлайны, сводки, карты интенсивности

**Критерии готовности:**

* Данные агрегируются по заданиям и проектам
* Есть API и UI-интерфейс для аналитики
* Поддерживается экспорт отчётов

---

### 2.9. Этап 9: Завершение и подготовка к релизу (2 недели)

**Задачи:**

1. **Финальный аудит и тестирование:**

   * Полный прогон функциональных и нагрузочных тестов
   * Проверка безопасности: JWT, доступы, SQL-инъекции, XSS
   * Проверка failover-сценариев и перезапуска

2. **Подготовка документации:**

   * Финальное обновление Docusaurus
   * Упрощённые инструкции для деплоя и использования
   * Чек-листы для QA и продакшн-релиза

3. **DevOps:**

   * Сборка релизных образов Docker
   * Настройка production-инфраструктуры (Kubernetes, облако, CI/CD)
   * Мониторинг и алерты на уровне production

**Критерии готовности:**

* Пройден финальный аудит и QA
* Подготовлены инструкции и документация
* CI/CD развертывает рабочую продакшн-версию
* Система стабильна под нагрузкой

---

### 2.10. Этап 10: Мониторинг, логирование и алертинг (1.5 недели)

**Задачи:**

1. **Интеграция мониторинга Prometheus + Grafana:**

   * Настройка `prometheus.yml` с `scrape_configs` для всех микросервисов
   * Экспозиция метрик `/metrics` в API Gateway, Crawler, Parser, Scheduler, File Processor
   * Визуализация через Grafana:

     * Панели CPU/Memory/Errors по сервисам
     * Графики распределения задач, таймлайны краулинга
     * Использование готовых dashboard-экспортов

2. **Настройка алертов:**

   * Правила в `alert.rules.yml` для:

     * HTTP 5xx ошибок
     * Повышенной задержки (latency > 1s)
     * Перегрузки очередей Redis
     * Отсутствия метрик от сервиса > 5 минут
   * Использование Alertmanager (email, Slack, Webhook)

3. **Структурированное логирование:**

   * Формат JSON: timestamp, level, message, service, trace\_id, context
   * Единый формат во всех сервисах (Go, Python, Node.js)
   * Логирование в stdout с последующей агрегацией через:

     * Loki (Grafana), либо
     * ElasticSearch + Filebeat (альтернатива)

4. **Трейсинг и распределённый контекст:**

   * Поддержка trace\_id в заголовках и логах
   * Возможная интеграция OpenTelemetry для визуального отображения запросов между сервисами

---

**Детальная реализация:**

#### Пример метрик для Crawler (FastAPI + aiohttp):

```python
from prometheus_client import Counter, Histogram, generate_latest
from fastapi import FastAPI, Request

crawler_requests_total = Counter("crawler_requests_total", "Total HTTP requests", ['method', 'endpoint'])
crawler_request_duration = Histogram("crawler_request_duration_seconds", "Request latency", ['endpoint'])

app = FastAPI()

@app.middleware("http")
async def prometheus_metrics(request: Request, call_next):
    import time
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time

    path = request.url.path
    crawler_requests_total.labels(request.method, path).inc()
    crawler_request_duration.labels(path).observe(process_time)

    return response

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

#### Пример структурированного лога (Go):

```go
logger.Info("Started crawling task", zap.String("url", task.URL), zap.Int("depth", task.Depth), zap.String("trace_id", traceID))
```

#### Пример alertrule:

```yaml
- alert: HighCrawlerErrorRate
  expr: rate(crawler_requests_total{code=~"5.."}[1m]) > 0.1
  for: 2m
  labels:
    severity: critical
  annotations:
    summary: "Высокий процент ошибок 5xx от Crawler"
    description: "Crawler возвращает слишком много 5xx за последние 2 минуты."
```

---

**Критерии готовности:**

* Все микросервисы отдают метрики Prometheus
* Grafana отображает дашборды в режиме реального времени
* Есть активные алерты по критическим событиям
* Логи унифицированы и пригодны для поиска и корреляции по trace\_id
* Вся инфраструктура логирования и мониторинга работает в Docker/Kubernetes окружении

---

Готов к продолжению этапов: логическая изоляция окружений, dev/staging/prod, поддержка версионирования API, мультиязычность и далее. Скажи, какой приоритет.


### 2.11. Этап 11: Разделение окружений и стабильность релизов (1 неделя)

**Задачи:**

1. **Разделение окружений:**

   * Поддержка трёх окружений: `development`, `staging`, `production`
   * Использование `.env` файлов и переменных окружения в Docker Compose и Kubernetes (`values.yaml`, Secrets/ConfigMaps)
   * Раздельные конфигурации CI/CD (GitHub Actions workflows с matrix/env vars)
   * Изоляция баз данных, Redis, S3 бакетов по окружениям

2. **Автоматизация релизов:**

   * Semver-версионирование по git-тегам (`v1.2.0`)
   * Генерация changelog (conventional commits + `auto-changelog`, `standard-version`)
   * CI-сборка и пуш в Docker registry с версией
   * Категории релизов: alpha, beta, stable

3. **Проверка на staging:**

   * Авторазвёртывание staging после merge в `develop`
   * Smoke-тесты и регрессии
   * Ручное подтверждение деплоя на `production`

**Критерии готовности:**

* Все сервисы поддерживают изолированные конфигурации по окружениям
* Сборка образов и деплой происходят по правилам CI
* Можно безопасно тестировать staging перед продакшен-релизом

---

**Детальная реализация:**

#### Пример GitHub Actions для релиза:

```yaml
name: Release CI

on:
  push:
    tags:
      - 'v*.*.*'

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Extract version
        run: echo "VERSION=${GITHUB_REF#refs/tags/v}" >> $GITHUB_ENV

      - name: Build Docker images
        run: |
          docker build -t yourorg/crawler-api-gateway:${VERSION} ./api-gateway
          docker build -t yourorg/crawler-parser:${VERSION} ./parser-service

      - name: Push images
        run: |
          echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
          docker push yourorg/crawler-api-gateway:${VERSION}
          docker push yourorg/crawler-parser:${VERSION}

      - name: Create GitHub release
        uses: softprops/action-gh-release@v1
        with:
          tag_name: ${{ github.ref }}
          name: "Release ${{ env.VERSION }}"
```

#### Пример структуры переменных окружения:

```env
# .env.staging
API_GATEWAY_URL=https://staging.crawler.io
POSTGRES_HOST=staging-db
REDIS_URL=redis://staging-redis:6379
S3_BUCKET_NAME=crawler-staging-data
ENVIRONMENT=staging
```

---

**Инфраструктурная поддержка:**

* Helm charts с `values-dev.yaml`, `values-staging.yaml`, `values-prod.yaml`
* Интеграция с ArgoCD или GitOps стратегией (опционально)

---

Готов перейти к следующим блокам: мультиязычность, доступ по ролям (RBAC), или визуальный редактор правил.

### 2.12. Этап 12: Мультиязычность и роли доступа (1.5 недели)

**Задачи:**

1. **Интерфейс мультиязычности (i18n):**

   * Использование i18n-фреймворков: `react-i18next` для фронтенда
   * Поддержка минимум двух языков: `ru`, `en`
   * Файлы перевода: `locales/en/*.json`, `locales/ru/*.json`
   * Механизм переключения языка в интерфейсе (dropdown + persist в localStorage)
   * Структура ключей: namespace → domain → элемент (например, `tasks.status.running`)

2. **Интернационализация сообщений API:**

   * Заголовок `Accept-Language` в запросах
   * Поддержка перевода ошибок и сообщений с использованием `gettext`, `i18n` middleware в FastAPI/Go

3. **Ролевая модель (RBAC):**

   * Роли: `admin`, `moderator`, `user`, `viewer`
   * Хранение прав в таблице `users(role)` и/или отдельной `permissions`
   * Middleware в API Gateway:

     * Проверка прав доступа по endpoint
     * Распределение разрешений (например, `can_create_project`, `can_delete_task`, `can_view_logs`)
   * UI-компоненты с проверкой доступа (например, `usePermissions()` hook)

**Критерии готовности:**

* Интерфейс переключается между `ru/en`, переводы покрывают UI и ошибки
* API корректно обрабатывает заголовок `Accept-Language`
* Реализовано разграничение прав в API и UI

---

**Детальная реализация:**

#### Пример структуры переводов:

```json
// locales/ru/tasks.json
{
  "status": {
    "running": "Выполняется",
    "pending": "В очереди",
    "completed": "Завершено",
    "failed": "Ошибка"
  }
}
```

```tsx
// components/TaskStatus.tsx
import { useTranslation } from 'react-i18next';

const TaskStatus = ({ status }: { status: string }) => {
  const { t } = useTranslation('tasks');
  return <span>{t(`status.${status}`)}</span>;
};
```

#### Пример проверки прав в Go:

```go
func RequirePermission(permission string) gin.HandlerFunc {
  return func(c *gin.Context) {
    userRole := c.GetString("role")
    if !IsAllowed(userRole, permission) {
      c.JSON(http.StatusForbidden, gin.H{"error": "Access denied"})
      c.Abort()
      return
    }
    c.Next()
  }
}

func IsAllowed(role, permission string) bool {
  switch role {
  case "admin": return true
  case "moderator": return permission != "delete_user"
  case "viewer": return permission == "view_only"
  default: return false
  }
}
```

#### Пример middleware Accept-Language (FastAPI):

```python
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

class LocaleMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        lang = request.headers.get("accept-language", "en").split(",")[0].lower()
        request.state.locale = lang if lang in ("ru", "en") else "en"
        response = await call_next(request)
        return response
```

---

**Дополнительно:**

* В админке UI можно отобразить список ролей и их права (editable matrix)
* Все ошибки API должны быть интернационализированы по ключу

---

### 2.13. Этап 13: Поддержка шаблонов конфигураций задач (1 неделя)

**Задачи:**

1. **Определение формата шаблона:**

   * Структура шаблона в JSON или YAML (например: имя, описание, глубина, правила парсинга, тип обхода, ограничения)
   * Типизация и валидация шаблонов через Pydantic или JSON Schema

2. **Хранилище шаблонов:**

   * Таблица `task_templates` в базе данных с полями: `name`, `description`, `config`, `visibility`, `owner_id`
   * Возможность приватных/публичных шаблонов

3. **Интерфейс создания/выбора шаблона:**

   * Форма создания нового шаблона на основе текущей конфигурации задачи
   * Возможность применения шаблона при создании новой задачи (dropdown/select)
   * Просмотр, редактирование и удаление шаблонов

4. **Импорт/экспорт:**

   * Кнопки "Экспорт шаблона" (в YAML/JSON)
   * Импорт шаблона из файла

---

**Критерии готовности:**

* Шаблоны сохраняются и доступны в БД
* Пользователь может создавать, применять и удалять шаблоны
* Интерфейс поддерживает визуальное применение шаблонов
* Работает экспорт/импорт шаблонов задач

---

**Пример шаблона в YAML:**

```yaml
name: Парсинг статей новостей
description: Шаблон для новостных сайтов
config:
  max_depth: 2
  start_urls:
    - "https://example.com/news"
  rules:
    - selector: "article h2 a"
      action: extract_link
    - selector: "article time"
      action: extract_date
  options:
    follow_links: true
    respect_robots_txt: true
```



### 2.13. Этап 13: Визуальный редактор правил парсинга (2 недели)

**Задачи:**

1. **Интерактивный UI-редактор:**

   * Использование React Flow для drag-and-drop построения логики извлечения
   * Узлы: "Selector", "Transform", "Filter", "Output"
   * Конфигурация каждого узла в форме справа (панель свойств)
   * Связи между узлами визуально отображают порядок применения

2. **Типы узлов и логика:**

   * Selector: CSS/XPath/Regex выборка элементов
   * Transform: очистка текста, trim, replace, extract
   * Filter: проверка по содержимому, регуляркам, длине
   * Output: имя поля, тип (текст, список, дата), валидация

3. **Сохранение и экспорт:**

   * Конвертация визуальной схемы в JSON/YAML правила
   * Автосохранение состояния (локально и в проекте)
   * Возможность ручной правки YAML под схемой

4. **Импорт существующих правил:**

   * Загрузка YAML и реконструкция графа узлов
   * Подсветка ошибок (например, недопустимые связи или конфликт ID)

5. **Preview-режим:**

   * Загрузка HTML-сниппета или URL
   * Подсветка выбранных элементов (selector highlight)
   * Применение текущей схемы к тестовой странице
   * Предпросмотр JSON-результата

---

**Критерии готовности:**

* Можно визуально собрать цепочку правила парсинга
* Схема сохраняется и загружается как YAML/JSON
* Preview показывает корректные результаты по HTML
* Импорт/экспорт работают без потерь

---

**Детальная реализация:**

#### Пример узлов:

```json
{
  "id": "node-1",
  "type": "selector",
  "data": {
    "selector_type": "css",
    "value": ".news-item h2"
  }
}
```

```yaml
- id: selector_title
  type: selector
  selector_type: css
  selector_value: ".title"
  next:
    - id: transform_clean

- id: transform_clean
  type: transform
  action: trim
  next:
    - id: output_title

- id: output_title
  type: output
  name: title
  field_type: text
```

#### Пример использования React Flow + Side Panel:

```tsx
const nodeTypes = {
  selector: SelectorNode,
  transform: TransformNode,
  filter: FilterNode,
  output: OutputNode,
};

<ReactFlow
  elements={elements}
  nodeTypes={nodeTypes}
  onNodeClick={(event, node) => setSelectedNode(node)}
/>

{selectedNode && (
  <SidePanel>
    <NodeEditor node={selectedNode} onChange={updateNode} />
  </SidePanel>
)}
```

---

**Дополнительно:**

* Возможность клонирования узлов
* Поддержка undo/redo
* Возможность группировки (subgraphs) и шаблонов узлов
* Модульность: позже — экспорт в docker-плагины или внешние обработчики

---

Готов перейти к этапу 14: поддержка шаблонов конфигураций задач, экспорт/импорт проектов, либо расширение DevOps-части. Уточни направление.


---

### 2.14. Этап 14: Визуальный просмотр логов и результатов (1.5 недели)

**Задачи:**

1. **Frontend-интерфейс логов:**

   * Таблица логов с фильтрами по дате, уровню (`INFO`, `WARN`, `ERROR`), сервису, trace\_id
   * Расширенный просмотр записи: request, response, stacktrace, контекст задачи
   * Возможность поиска по тексту и сохранения фильтров
   * Пагинация и виртуализация при больших объёмах (например, `react-window`)

2. **Визуализация результатов парсинга:**

   * Таблица результатов: URL, заголовок, дата, ключевые поля
   * Карточки с табами: сырой контент, структурированные данные, JSON, preview
   * Ссылки на скачанные файлы и изображения

3. **Трассировка по trace\_id:**

   * Возможность проследить путь запроса между сервисами
   * Связка логов: crawler → parser → file-processor
   * Использование общего trace\_id из логирования (см. этап мониторинга)

4. **Реализация API:**

   * Методы для получения логов, результатов, статуса задачи
   * Пагинация, сортировка, фильтрация на уровне API

---

**Критерии готовности:**

* Интерфейс логов с фильтрами, деталями и трассировкой работает корректно
* Результаты парсинга доступны в структурированном виде
* API отдаёт данные с учётом прав пользователя (RBAC)

---

Следующий шаг: поддержка коллаборации в проектах, расширение структуры прав или настройка мультитенантности. Уточни приоритет.










