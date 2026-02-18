from pydantic import BaseModel, HttpUrl
from typing import Optional, List, Literal
from datetime import datetime

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

# Вложенные модели
class FieldSchema(BaseModel):
    name: str
    selector: str
    type: Literal["text", "number", "link", "image"]
    example: Optional[str] = None
    attribute: Optional[str] = None

class PaginationSchema(BaseModel):
    type: Literal["next_button", "scroll", "url_pattern"]
    selector: Optional[str] = None
    url_template: Optional[str] = None

class ConfigData(BaseModel):
    container_selector: str
    fields: List[FieldSchema]
    pagination: Optional[PaginationSchema] = None

# Для создания
class ConfigCreate(BaseModel):
    domain: str
    url_pattern: Optional[str] = None
    config: ConfigData
    user_id: Optional[int] = None

# Для чтения
class ConfigRead(BaseModel):
    id: int
    domain: str
    url_pattern: Optional[str]
    config: ConfigData
    created_at: datetime
    updated_at: Optional[datetime]
    user_id: Optional[int]

    class Config:
        orm_mode = True