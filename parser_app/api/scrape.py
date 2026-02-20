import asyncio
import json
import uuid
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import FileResponse

from services.exporter.exporter import Exporter
from core.database import get_db
from core.redis_client import get_redis
from core.schemas import ScrapeStartRequest, ScrapeStatusResponse
from models.config import ParserConfig
from tasks.scrape_tasks import run_scrape_task

router = APIRouter(prefix="/scrape", tags=["scrape"])

@router.post("/start")
async def start_scrape(req: ScrapeStartRequest, db: AsyncSession = Depends(get_db)):
    task_id = str(uuid.uuid4())
    if req.config_id:
        config = await db.get(ParserConfig, req.config_id)
        if not config:
            raise HTTPException(404, "Config not found")
    else:
        raise HTTPException(400, "config_id required")

    redis = await get_redis()
    await redis.setex(f"scrape:{task_id}:status", 3600, "PENDING")
    asyncio.create_task(run_scrape_task(task_id, req.config_id, str(req.start_url), req.max_pages))
    return {"task_id": task_id}

@router.get("/status/{task_id}", response_model=ScrapeStatusResponse)
async def scrape_status(task_id: str):
    redis = await get_redis()
    status = await redis.get(f"scrape:{task_id}:status")
    if not status:
        raise HTTPException(404, "Task not found")
    pages = await redis.get(f"scrape:{task_id}:pages") or 0
    items = await redis.get(f"scrape:{task_id}:items") or 0
    error = await redis.get(f"scrape:{task_id}:error")
    return ScrapeStatusResponse(
        task_id=task_id,
        status=status,
        pages_processed=int(pages),
        items_count=int(items),
        error=error
    )

@router.get("/result/{task_id}")
async def scrape_result(task_id: str):
    redis = await get_redis()
    data_json = await redis.get(f"scrape:{task_id}:data")
    if not data_json:
        raise HTTPException(404, "Result not ready or not found")
    data = json.loads(data_json)
    return {"task_id": task_id, "data": data, "total_items": len(data)}

@router.get("/export/{task_id}")
async def export_results(task_id: str, format: str = "json"):
    """
    Экспортирует результаты задачи сбора в JSON или Excel.
    Параметр format: 'json' (по умолчанию) или 'excel'.
    """
    redis = await get_redis()
    data_json = await redis.get(f"scrape:{task_id}:data")
    if not data_json:
        raise HTTPException(404, "Данные не найдены или задача ещё не завершена")

    data = json.loads(data_json)

    if format.lower() == "json":
        file_path = Exporter.to_json(data)
        media_type = "application/json"
        download_filename = f"results_{task_id}.json"
    elif format.lower() == "excel":
        file_path = Exporter.to_excel(data)
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        download_filename = f"results_{task_id}.xlsx"
    else:
        raise HTTPException(400, "Неподдерживаемый формат. Используйте 'json' или 'excel'.")

    return FileResponse(
        path=file_path,
        media_type=media_type,
        filename=download_filename
    )

@router.get("/needs-update/{task_id}")
async def scrape_needs_update(task_id: str):
    redis = await get_redis()
    update_required = await redis.get(f"scrape:{task_id}:update_required")
    return {"task_id": task_id, "update_required": update_required == "true"}