from playwright.sync_api import sync_playwright
from lxml import html
from urllib.parse import urljoin
from typing import List, Dict, Any, Optional
from core.schemas import ConfigData
from .exceptions import NoContainerFound, NoFieldsExtracted

class SyncScraper:
    def __init__(self, config: ConfigData, start_url: str, max_pages: Optional[int] = None):
        self.config = config
        self.start_url = start_url
        self.max_pages = max_pages
        self.results = []
        self.pages_processed = 0

    def run(self) -> List[Dict[str, Any]]:
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
        tree = html.fromstring(content)
        containers = tree.cssselect(self.config.container_selector)
        if not containers:
            raise NoContainerFound(
                f"Container selector '{self.config.container_selector}' not found on page {self.pages_processed + 1}"
            )
        page_items = []
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

        if not page_items:
            raise NoFieldsExtracted("No items extracted from containers")
        self.results.extend(page_items)

    def _has_next_page(self, page) -> bool:
        pagination = self.config.pagination
        if not pagination:
            return False
        if pagination.type == 'next_button':
            button = page.query_selector(pagination.selector)
            return button is not None and button.is_visible()
        elif pagination.type == 'scroll':
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
        elif pagination.type == 'scroll':
            last_height = page.evaluate("document.body.scrollHeight")
            while True:
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                import time
                time.sleep(2)
                new_height = page.evaluate("document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
        elif pagination.type == 'url_pattern':
            next_url = pagination.url_template.replace("{page}", str(self.pages_processed + 2))
            page.goto(next_url, wait_until="networkidle")