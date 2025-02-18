from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class PagingBase(BaseModel):
    total: Optional[int] = Field(default=None, description="总记录数", ge=0)
    page: int = Field(..., description="当前页码", ge=1)
    limit: int = Field(..., description="每页显示的记录数", ge=1)
    next: bool = Field(default=False, description="是否有下一页")
