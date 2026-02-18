from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from core.database import get_db
from models.config import ParserConfig
from core.schemas import ConfigCreate, ConfigRead
import logging

router = APIRouter(prefix="/configs", tags=["configs"])
logger = logging.getLogger(__name__)

@router.post("/", response_model=ConfigRead)
async def create_config(config: ConfigCreate, db: AsyncSession = Depends(get_db)):
    db_config = ParserConfig(
        domain=config.domain,
        url_pattern=config.url_pattern,
        config=config.config.dict(),
        user_id=config.user_id
    )
    db.add(db_config)
    await db.commit()
    await db.refresh(db_config)
    return db_config

@router.get("/", response_model=List[ConfigRead])
async def list_configs(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ParserConfig))
    configs = result.scalars().all()
    return configs

@router.get("/{config_id}", response_model=ConfigRead)
async def get_config(config_id: int, db: AsyncSession = Depends(get_db)):
    config = await db.get(ParserConfig, config_id)
    if not config:
        raise HTTPException(404, "Config not found")
    return config

@router.get("/by-domain/", response_model=List[ConfigRead])
async def get_configs_by_domain(domain: str, db: AsyncSession = Depends(get_db)):
    stmt = select(ParserConfig).where(ParserConfig.domain == domain)
    result = await db.execute(stmt)
    configs = result.scalars().all()
    return configs