import uuid
from datetime import datetime, timezone
from typing import Optional, Union, Dict, List

from sqlalchemy.orm import mapped_column, DeclarativeBase, Mapped
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Integer,
    MetaData,
    String,
    SmallInteger,
    Float,
    BigInteger,
    Table,
    text, Index, Enum, CheckConstraint, func, JSON
)
import enum

from app.core.database import Base


class QueryData(Base):
    __tablename__ = 'query_data'
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    parameter: Mapped[Union[Dict, List]] = mapped_column(JSON, nullable=False)
    create_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    update_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), index=True)
