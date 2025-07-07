import asyncio
from dataclasses import dataclass
from typing import List, Optional
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser
import aiohttp
from bs4 import BeautifulSoup

@dataclass
class CrawlResult:
    url: str
    status: int
    content: str
    links: List[str]

class SimpleCrawler:
    def __init__(self, delay: float = 1.0, max_connections: int = 10):
        self.delay = delay
        self.semaphore = asyncio.Semaphore(max_connections)
        self.last_request = {}
        self.session: Optional[aiohttp.ClientSession] = None
        self.robots: dict[str, RobotFileParser] = {}

    async def __aenter__(self):
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(timeout=timeout)
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if self.session:
            await self.session.close()

    async def _respect_robots(self, url: str) -> bool:
        parsed = urlparse(url)
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        if robots_url not in self.robots:
            rp = RobotFileParser()
            try:
                async with self.session.get(robots_url) as resp:
                    if resp.status == 200:
                        rp.parse((await resp.text()).splitlines())
                    else:
                        rp = None
            except Exception:
                rp = None
            self.robots[robots_url] = rp
        rp = self.robots[robots_url]
        if rp is None:
            return True
        return rp.can_fetch("*", url)

    async def _wait_delay(self, domain: str):
        last = self.last_request.get(domain)
        if last:
            diff = asyncio.get_event_loop().time() - last
            if diff < self.delay:
                await asyncio.sleep(self.delay - diff)
        self.last_request[domain] = asyncio.get_event_loop().time()

    async def fetch(self, url: str) -> Optional[CrawlResult]:
        parsed = urlparse(url)
        if not await self._respect_robots(url):
            return None
        await self._wait_delay(parsed.netloc)
        async with self.semaphore:
            try:
                async with self.session.get(url) as resp:
                    text = await resp.text()
                    links = self.extract_links(text, url)
                    return CrawlResult(url=str(resp.url), status=resp.status, content=text, links=links)
            except Exception:
                return None

    def extract_links(self, html: str, base: str) -> List[str]:
        soup = BeautifulSoup(html, "html.parser")
        links = []
        for tag in soup.find_all('a'):
            href = tag.get('href')
            if href:
                absolute = urljoin(base, href)
                if urlparse(absolute).scheme in ("http", "https"):
                    links.append(absolute)
        return links

async def crawl(start_url: str, depth: int = 1):
    seen = set()
    queue = [(start_url, 0)]
    async with SimpleCrawler() as crawler:
        while queue:
            url, d = queue.pop(0)
            if url in seen or d > depth:
                continue
            seen.add(url)
            result = await crawler.fetch(url)
            if result:
                print(f"Fetched {result.url} ({result.status})")
                if d < depth:
                    for link in result.links:
                        if link not in seen:
                            queue.append((link, d + 1))

if __name__ == "__main__":
    import sys
    start = sys.argv[1] if len(sys.argv) > 1 else "https://example.com"
    asyncio.run(crawl(start, depth=1))
