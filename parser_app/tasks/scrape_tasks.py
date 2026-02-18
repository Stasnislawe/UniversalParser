import asyncio
import json
import logging
from sqlalchemy import select

from core.redis_client import get_redis
from core.schemas import ConfigData
from services.scraper.scraper import SyncScraper
from models.config import ParserConfig
from core.database import AsyncSessionLocal

logger = logging.getLogger(__name__)

async def run_scrape_task(task_id: str, config_id: int, start_url: str, max_pages: int = None):
    redis = await get_redis()
    try:
        # Загружаем конфигурацию из БД
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(ParserConfig).where(ParserConfig.id == config_id))
            config_model = result.scalar_one_or_none()
            if not config_model:
                raise ValueError(f"Config {config_id} not found")
            config_data = ConfigData(**config_model.config)

        # Обновляем статус
        await redis.setex(f"scrape:{task_id}:status", 3600, "PROCESSING")
        await redis.setex(f"scrape:{task_id}:pages", 3600, "0")
        await redis.setex(f"scrape:{task_id}:items", 3600, "0")

        # Запускаем синхронный скрапер в отдельном потоке
        scraper = SyncScraper(config_data, start_url, max_pages)
        results = await asyncio.to_thread(scraper.run)

        # Сохраняем результаты
        await redis.setex(f"scrape:{task_id}:data", 3600, json.dumps(results))
        await redis.setex(f"scrape:{task_id}:pages", 3600, str(scraper.pages_processed))
        await redis.setex(f"scrape:{task_id}:items", 3600, str(len(results)))
        await redis.setex(f"scrape:{task_id}:status", 3600, "SUCCESS")
        logger.info(f"Scrape task {task_id} completed, {len(results)} items")

    except Exception as e:
        logger.exception(f"Scrape task {task_id} failed")
        await redis.setex(f"scrape:{task_id}:status", 3600, "FAILURE")
        await redis.setex(f"scrape:{task_id}:error", 3600, str(e))