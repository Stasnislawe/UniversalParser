import asyncio
from urllib.parse import urlparse

from fastapi import APIRouter, BackgroundTasks, HTTPException, Depends
from core.schemas import (FetchRequest, TaskResponse, TaskStatusResponse, PageData, CandidatesResponse, Candidate,
                          SelectContainerRequest, FieldsResponse, Field)
from services.fetcher import fetch
from services.analyzer.field_extractor import extract_fields_from_blocks
from services.analyzer.structure import find_repeating_blocks
from core.redis_client import get_redis
from core.database import get_db
from models.config import ParserConfig
from lxml import html
import uuid
import json
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter(prefix="/analyze", tags=["analyze"])
logger = logging.getLogger(__name__)


async def process_analysis(task_id: str, url: str, use_js: bool):
    """Фоновая задача: загружает страницу, анализирует структуру, сохраняет результаты."""
    redis = await get_redis()
    try:
        page_data = await fetch(url, use_js)
        # Анализируем структуру
        candidates = find_repeating_blocks(page_data.html)
        # Сохраняем результат страницы
        await redis.setex(f"task:{task_id}:result", 3600, page_data.json())
        # Сохраняем кандидатов
        candidates_json = json.dumps([c.dict() for c in candidates])
        await redis.setex(f"session:{task_id}:candidates", 3600, candidates_json)
        await redis.setex(f"task:{task_id}:status", 3600, "SUCCESS")
        logger.info(f"Task {task_id} completed, found {len(candidates)} candidate groups.")
    except Exception as e:
        logger.exception(f"Task {task_id} failed")
        await redis.setex(f"task:{task_id}:status", 3600, "FAILURE")
        await redis.setex(f"task:{task_id}:error", 3600, str(e))


@router.post("/start", response_model=TaskResponse)
async def start_analysis(
    req: FetchRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    domain = urlparse(str(req.url)).netloc
    # Проверяем существующие конфигурации
    stmt = select(ParserConfig).where(ParserConfig.domain == domain)
    result = await db.execute(stmt)
    existing = result.scalars().first()
    if existing:
        logger.info(f"Found existing config for domain {domain}: {existing.id}")

    task_id = str(uuid.uuid4())
    background_tasks.add_task(process_analysis, task_id, str(req.url), req.use_js)
    redis = await get_redis()
    await redis.setex(f"task:{task_id}:status", 3600, "PENDING")
    return TaskResponse(task_id=task_id)



@router.get("/status/{task_id}", response_model=TaskStatusResponse)
async def get_status(task_id: str):
    redis = await get_redis()
    status = await redis.get(f"task:{task_id}:status")
    if not status:
        raise HTTPException(status_code=404, detail="Task not found")

    response = TaskStatusResponse(task_id=task_id, status=status)
    if status == "SUCCESS":
        # Можно не возвращать весь HTML, только session_id
        response.session_id = task_id
    elif status == "FAILURE":
        error = await redis.get(f"task:{task_id}:error")
        response.error = error
    return response


@router.get("/candidates/{session_id}", response_model=CandidatesResponse)
async def get_candidates(session_id: str):
    redis = await get_redis()
    candidates_json = await redis.get(f"session:{session_id}:candidates")
    if not candidates_json:
        raise HTTPException(status_code=404, detail="Candidates not found")
    candidates = [Candidate(**item) for item in json.loads(candidates_json)]
    return CandidatesResponse(session_id=session_id, candidates=candidates)


async def extract_fields_task(session_id: str, container_selector: str):
    logger.info(f"🔥 extract_fields_task started for session {session_id}")
    redis = await get_redis()
    try:
        page_data_json = await redis.get(f"task:{session_id}:result")
        if not page_data_json:
            raise Exception("Page data not found")
        page_data = PageData.parse_raw(page_data_json)

        tree = await asyncio.to_thread(html.fromstring, page_data.html)
        containers = await asyncio.to_thread(tree.cssselect, container_selector)
        logger.info(f"Found {len(containers)} containers for selector '{container_selector}'")
        if not containers:
            raise Exception(f"Container selector '{container_selector}' not found")

        blocks_html = []
        container = containers[0]
        for child in container.iterchildren():
            if not isinstance(child, html.HtmlElement):
                continue
            if child.tag in ['script', 'style', 'noscript']:
                continue
            blocks_html.append(html.tostring(child, encoding='unicode'))
            if len(blocks_html) >= 5:
                break

        logger.info(f"Extracted {len(blocks_html)} blocks from container")
        if not blocks_html:
            raise Exception("No blocks found inside container")

        fields = extract_fields_from_blocks(blocks_html)
        logger.info(f"🔥 fields extracted: {len(fields)} items")
        if isinstance(fields, list):
            for i, f in enumerate(fields):
                logger.info(f"  Field {i}: {f.dict()}")
        else:
            logger.error(f"Expected list, got {type(fields)}")

        fields_json = json.dumps([f.dict() for f in fields])
        await redis.setex(f"session:{session_id}:fields", 3600, fields_json)
        saved = await redis.get(f"session:{session_id}:fields")
        logger.info(f"Saved in redis: {saved}")

        await redis.setex(f"session:{session_id}:container", 3600, container_selector)
        logger.info(f"✅ Fields extracted and saved for {session_id}")

    except Exception as e:
        logger.exception(f"Field extraction failed for session {session_id}")
        await redis.setex(f"session:{session_id}:fields_error", 3600, str(e))


@router.post("/select-container")
async def select_container(req: SelectContainerRequest):
    session_id = req.session_id
    container_selector = req.container_selector

    redis = await get_redis()
    exists = await redis.exists(f"session:{session_id}:candidates")
    if not exists:
        raise HTTPException(status_code=404, detail="Session not found")

    # Прямой вызов (не фоновый) – для отладки, или можно вернуть background_tasks.add_task
    # Если нужно быстро получить результат, лучше await
    await extract_fields_task(session_id, container_selector)

    return {"status": "done", "session_id": session_id}


@router.get("/fields/{session_id}", response_model=FieldsResponse)
async def get_fields(session_id: str):
    """Получить извлечённые поля для сессии."""
    redis = await get_redis()
    fields_json = await redis.get(f"session:{session_id}:fields")
    error = await redis.get(f"session:{session_id}:fields_error")
    print(f"Retrieved from redis: {fields_json}")

    if error:
        # Возвращаем ошибку, которая произошла в задаче
        raise HTTPException(status_code=500, detail=error.decode('utf-8') if isinstance(error, bytes) else error)

    if not fields_json:
        raise HTTPException(status_code=404, detail="Fields not ready or not found. Try again later.")

    fields = [Field(**item) for item in json.loads(fields_json)]
    return FieldsResponse(session_id=session_id, fields=fields)