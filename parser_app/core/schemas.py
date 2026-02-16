from pydantic import BaseModel, HttpUrl
from typing import Optional

class FetchRequest(BaseModel):
    url: HttpUrl
    use_js: bool = True

class PageData(BaseModel):
    url: str
    final_url: str
    html: str
    title: Optional[str] = None
    screenshot: Optional[str] = None  # base64

class TaskResponse(BaseModel):
    task_id: str

class TaskStatusResponse(BaseModel):
    task_id: str
    status: str  # "PENDING", "SUCCESS", "FAILURE"
    result: Optional[PageData] = None
    error: Optional[str] = None