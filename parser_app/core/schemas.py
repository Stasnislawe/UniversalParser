from pydantic import BaseModel, HttpUrl
from typing import Optional, List

class FetchRequest(BaseModel):
    url: HttpUrl
    use_js: bool = True

class PageData(BaseModel):
    url: str
    final_url: str
    html: str
    title: Optional[str] = None
    screenshot: Optional[str] = None  # base64

class Candidate(BaseModel):
    id: int
    container_selector: str
    example_items: List[str]
    count: int

class CandidatesResponse(BaseModel):
    session_id: str
    candidates: List[Candidate]

class TaskResponse(BaseModel):
    task_id: str

class TaskStatusResponse(BaseModel):
    task_id: str
    status: str  # "PENDING", "SUCCESS", "FAILURE"
    session_id: Optional[str] = None  # если статус SUCCESS
    result: Optional[PageData] = None  # опционально, может не возвращать весь HTML
    error: Optional[str] = None