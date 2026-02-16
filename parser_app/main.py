import sys
if sys.platform == "win32":
    import asyncio
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from fastapi import FastAPI
from contextlib import asynccontextmanager
from core.redis_client import close_redis
from api import analyze
import logging

logging.basicConfig(level=logging.INFO)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    yield
    # Shutdown
    await close_redis()
    logging.info("Redis closed")

app = FastAPI(title="Parser App", lifespan=lifespan)
app.include_router(analyze.router, prefix="/api")