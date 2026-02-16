import pytest
from core.schemas import PageData
from services.fetcher import fetch


@pytest.mark.asyncio
async def test_fetch_httpx():
    page = await fetch("https://example.com", use_js=False)
    assert isinstance(page, PageData)
    assert "Example Domain" in page.html
    assert page.final_url == "https://example.com/"