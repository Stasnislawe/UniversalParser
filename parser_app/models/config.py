from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.sql import func
from core.database import Base

class ParserConfig(Base):
    __tablename__ = "parser_configs"

    id = Column(Integer, primary_key=True, index=True)
    domain = Column(String, nullable=False, index=True)
    url_pattern = Column(String, nullable=True)
    config = Column(JSON, nullable=False)  # содержит container_selector, fields, pagination
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    user_id = Column(Integer, nullable=True)