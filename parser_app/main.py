import sys
if sys.platform == "win32":
    import asyncio
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
from fastapi import FastAPI
from contextlib import asynccontextmanager
from core.redis_client import close_redis
from api import analyze, configs, scrape
from core.database import engine, Base
import logging

def handle_exception(loop, context):
    msg = context.get("exception", context["message"])
    logging.error(f"Caught exception: {msg}")

loop = asyncio.get_event_loop()
loop.set_exception_handler(handle_exception)

logging.basicConfig(level=logging.INFO)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown
    await close_redis()
    await engine.dispose()
    logging.info("Redis closed, DB engine disposed")

app = FastAPI(title="Parser App", lifespan=lifespan)
app.include_router(analyze.router, prefix="/api")
app.include_router(configs.router, prefix="/api")
app.include_router(scrape.router, prefix="/api")