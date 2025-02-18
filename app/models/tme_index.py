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


class TmeIndexType(enum.Enum):
    GROUP = 'group'
    CHANNEL = 'channel'
    BOT = 'bot'


class TmeIndex(Base):
    __tablename__ = 'tme_index'
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    username: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True)
    type: Mapped[TmeIndexType] = mapped_column(Enum(TmeIndexType, length=32), nullable=False, index=True)
    nickname: Mapped[str] = mapped_column(String(255), nullable=False)
    desc: Mapped[str] = mapped_column(String(255), nullable=False)
    count_members: Mapped[int] = mapped_column(Integer, default=0)
    count_view: Mapped[int] = mapped_column(Integer, default=0)
    invalid_at: Mapped[Optional[datetime]] = mapped_column(DateTime, index=True)
    last_gather_at: Mapped[Optional[datetime]] = mapped_column(DateTime, index=True)
    create_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    update_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), index=True)
