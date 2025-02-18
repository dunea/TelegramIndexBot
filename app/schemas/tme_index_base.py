from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, List
from app.models import TmeIndex, TmeIndexType  # 假设 TmeIndex 和 TmeIndexType 已定义
from app.schemas.paging_base import PagingBase


# Pydantic模型
class TmeIndexBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    username: str
    type: TmeIndexType
    nickname: str
    desc: str
    count_members: int
    count_view: int
    invalid_at: Optional[datetime]
    last_gather_at: Optional[datetime]
    create_at: datetime
    update_at: datetime


class TmeIndexBaseList(PagingBase):
    list: List[TmeIndexBase]


# 用于返回的模型
class TmeIndexResponse(TmeIndexBase):
    pass


# 用于接收和创建的模型
class TmeIndexCreate(BaseModel):
    type: TmeIndexType = Field(...)
    username: str = Field(...)
    nickname: str = Field(...)
    desc: str = Field(default=0)
    count_members: int = Field(...)
