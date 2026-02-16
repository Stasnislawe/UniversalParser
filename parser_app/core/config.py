from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    redis_url: str = "redis://localhost:6379/0"
    environment: str = "development"
    log_level: str = "INFO"
    playwright_headless: bool = True
    cache_ttl_seconds: int = 3600  # 1 час

    class Config:
        env_file = ".env"

settings = Settings()