from fastapi import APIRouter, Depends, HTTPException, Query, Form

from app import schemas
from app.core.di import di
from app.services import IndexService

index_route = APIRouter()


# 添加索引于详细信息
@index_route.post("/add_index_by_detail")
async def add_index_by_detail(request: schemas.TmeIndexCreate):
    index_svc = di.get(IndexService)
    return index_svc.add_index_by_detail(detail=request)
