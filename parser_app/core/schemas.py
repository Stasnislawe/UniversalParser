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

# Запрос на запуск сбора
class ScrapeStartRequest(BaseModel):
    config_id: Optional[int] = None          # можно использовать сохранённую конфигурацию
    config: Optional[ConfigData] = None      # или передать конфигурацию напрямую
    start_url: HttpUrl
    max_pages: Optional[int] = None          # ограничение по страницам

# Статус задачи сбора
class ScrapeStatusResponse(BaseModel):
    task_id: str
    status: str  # "PENDING", "PROCESSING", "SUCCESS", "FAILURE"
    pages_processed: Optional[int] = None
    items_count: Optional[int] = None
    error: Optional[str] = None

# Результат сбора (список записей)
class ScrapeResult(BaseModel):
    task_id: str
    data: List[dict]
    total_items: int