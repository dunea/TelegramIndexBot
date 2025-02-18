from fastapi import APIRouter, Depends, HTTPException, Query, Form

from app import schemas
from app.api.middlewares.verify_key import verify_key
from app.core.di import di
from app.services import IndexService

index_route = APIRouter()


# 添加索引于详细信息
@index_route.post("/add_index_by_detail")
async def add_index_by_detail(request: schemas.TmeIndexCreate, api_key: str = Depends(verify_key)):
    index_svc = di.get(IndexService)
    return index_svc.add_index_by_detail(detail=request)


# 删除索引于ID
@index_route.delete("/del_index_by_id/{_id}")
async def del_index_by_id(_id: str, api_key: str = Depends(verify_key)):
    index_svc = di.get(IndexService)
    index_svc.del_index_by_id(_id)
    return
