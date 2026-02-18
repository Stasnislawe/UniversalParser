import time
import logging
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin

from playwright.sync_api import sync_playwright
from lxml import html as lxml_html

from core.schemas import ConfigData, FieldSchema, PaginationSchema

logger = logging.getLogger(__name__)

class SyncScraper:
    def __init__(self, config: ConfigData, start_url: str, max_pages: Optional[int] = None):
        self.config = config
        self.start_url = start_url
        self.max_pages = max_pages
        self.results: List[Dict[str, Any]] = []
        self.pages_processed = 0

    def run(self) -> List[Dict[str, Any]]:
        """Синхронный метод для сбора данных."""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            try:
                page.goto(self.start_url, wait_until="networkidle", timeout=30000)
                self._extract_page_data(page)
                self.pages_processed += 1

                while self._has_next_page(page):
                    if self.max_pages and self.pages_processed >= self.max_pages:
                        break
                    self._perform_pagination(page)
                    page.wait_for_load_state("networkidle")
                    self._extract_page_data(page)
                    self.pages_processed += 1
            finally:
                page.close()
                browser.close()
        return self.results

    def _extract_page_data(self, page):
        content = page.content()
        tree = lxml_html.fromstring(content)
        containers = tree.cssselect(self.config.container_selector)
        logger.info(f"Found {len(containers)} containers on page {self.pages_processed+1}")

        for container in containers:
            item = {}
            for field in self.config.fields:
                elements = container.cssselect(field.selector)
                if elements:
                    el = elements[0]
                    if field.type in ('text', 'number'):
                        value = el.text_content().strip()
                    elif field.type == 'link':
                        value = el.get('href')
                        if value and not value.startswith(('http://', 'https://')):
                            value = urljoin(page.url, value)
                    elif field.type == 'image':
                        value = el.get('src')
                        if value and not value.startswith(('http://', 'https://')):
                            value = urljoin(page.url, value)
                    else:
                        value = None
                else:
                    value = None
                item[field.name] = value
            self.results.append(item)

    def _has_next_page(self, page) -> bool:
        pagination = self.config.pagination
        if not pagination:
            return False
        if pagination.type == 'next_button':
            button = page.query_selector(pagination.selector)
            return button is not None and button.is_visible()
        elif pagination.type == 'scroll':
            # Всегда пытаемся скроллить, логика остановки внутри _perform_pagination
            return True
        elif pagination.type == 'url_pattern':
            return True
        return False

    def _perform_pagination(self, page):
        pagination = self.config.pagination
        if not pagination:
            return
        if pagination.type == 'next_button':
            page.click(pagination.selector)
            page.wait_for_load_state("networkidle")
        elif pagination.type == 'scroll':
            last_height = page.evaluate("document.body.scrollHeight")
            while True:
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(2)  # синхронная задержка
                new_height = page.evaluate("document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
        elif pagination.type == 'url_pattern':
            next_url = pagination.url_template.replace("{page}", str(self.pages_processed + 2))
            page.goto(next_url, wait_until="networkidle")