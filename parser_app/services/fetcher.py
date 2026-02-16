import hashlib
import httpx
import asyncio
from playwright.sync_api import sync_playwright
from core.schemas import PageData
from core.redis_client import get_redis
from core.config import settings
import logging

logger = logging.getLogger(__name__)

def fetch_playwright_sync(url: str) -> PageData:
    """Синхронная функция для загрузки страницы через Playwright."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()
        try:
            page.goto(url, wait_until="networkidle", timeout=30000)
            html = page.content()
            title = page.title()
            return PageData(
                url=url,
                final_url=page.url,
                html=html,
                title=title
            )
        finally:
            page.close()
            context.close()
            browser.close()

async def fetch_httpx(url: str) -> PageData:
    async with httpx.AsyncClient(follow_redirects=True) as client:
        resp = await client.get(url, timeout=30)
        resp.raise_for_status()
        return PageData(
            url=url,
            final_url=str(resp.url),
            html=resp.text,
            title=None
        )

async def fetch(url: str, use_js: bool = True) -> PageData:
    redis = await get_redis()
    cache_key = f"page:{hashlib.md5(url.encode()).hexdigest()}"
    cached = await redis.get(cache_key)
    if cached:
        logger.info(f"Cache hit for {url}")
        return PageData.parse_raw(cached)

    logger.info(f"Fetching {url} with use_js={use_js}")
    try:
        if use_js:
            # Запускаем синхронную функцию в отдельном потоке
            page_data = await asyncio.to_thread(fetch_playwright_sync, url)
        else:
            page_data = await fetch_httpx(url)
    except Exception as e:
        logger.error(f"Error fetching {url}: {e}")
        raise

    await redis.setex(cache_key, settings.cache_ttl_seconds, page_data.json())
    return page_data