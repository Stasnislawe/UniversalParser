from fastapi import APIRouter, BackgroundTasks, HTTPException
from core.schemas import FetchRequest, TaskResponse, TaskStatusResponse, PageData, CandidatesResponse, Candidate
from services.fetcher import fetch
from services.analyzer.structure import find_repeating_blocks
from core.redis_client import get_redis
import uuid
import json
import logging

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
async def start_analysis(req: FetchRequest, background_tasks: BackgroundTasks):
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
        # По желанию можно также вернуть страницу (но это тяжело)
        # result_data = await redis.get(f"task:{task_id}:result")
        # if result_data:
        #     response.result = PageData.parse_raw(result_data)
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