# web-parser-py

This repository contains a minimal Python crawler example. It uses `aiohttp`
for asynchronous HTTP requests and `BeautifulSoup` for HTML parsing. The
`SimpleCrawler` class respects `robots.txt`, applies a configurable delay
between requests per domain and extracts links for recursive crawling.

## Usage

Install dependencies and run the crawler with a start URL:

```bash
pip install aiohttp beautifulsoup4
python -m crawler.web_parser https://example.com
```

The crawler visits the start page, prints the fetched URL and status code and
optionally crawls discovered links up to the specified depth.
