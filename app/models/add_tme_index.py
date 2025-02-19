import uuid
from datetime import datetime, timezone
from typing import Optional

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
    text, Index, Enum, CheckConstraint, func,
)
import enum

from app.core.database import Base


class AddTmeIndex(Base):
    __tablename__ = 'add_tme_index'
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    username: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    user_chat_id: Mapped[Optional[int]] = mapped_column(BigInteger, index=True)
    gather_at: Mapped[Optional[datetime]] = mapped_column(DateTime, index=True)
    create_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    update_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), index=True)
