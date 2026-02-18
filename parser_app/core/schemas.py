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

# Кандидаты
class Candidate(BaseModel):
    id: int
    container_selector: str
    example_items: List[str]
    count: int

class CandidatesResponse(BaseModel):
    session_id: str
    candidates: List[Candidate]

# Задачи
class TaskResponse(BaseModel):
    task_id: str

class TaskStatusResponse(BaseModel):
    task_id: str
    status: str  # "PENDING", "SUCCESS", "FAILURE"
    session_id: Optional[str] = None  # если статус SUCCESS
    result: Optional[PageData] = None  # опционально, может не возвращать весь HTML
    error: Optional[str] = None

# Поле
class Field(BaseModel):
    name: str
    selector: str
    type: str  # "text", "number", "link", "image"
    example: Optional[str] = None
    attribute: Optional[str] = None  # для ссылок и картинок

class SelectContainerRequest(BaseModel):
    session_id: str
    container_selector: str

class FieldsResponse(BaseModel):
    session_id: str
    fields: List[Field]