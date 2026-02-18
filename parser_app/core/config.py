from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    redis_url: str = "redis://localhost:6379/0"
    database_url: str = "postgresql+asyncpg://postgres:password@localhost/parser_db"
    environment: str = "development"
    log_level: str = "INFO"
    playwright_headless: bool = True
    cache_ttl_seconds: int = 3600

    class Config:
        env_file = ".env"

settings = Settings()