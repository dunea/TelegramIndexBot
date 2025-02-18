from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException


async def exception_handler(request: Request, exc: Exception):
    if isinstance(exc, ValueError):
        return JSONResponse(
            status_code=400,
            content={"detail": str(exc)},
        )
    elif isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )
    elif isinstance(exc, StarletteHTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )
    elif isinstance(exc, RequestValidationError):
        return JSONResponse(
            status_code=422,
            content={"detail": "请求参数验证失败", "errors": exc.errors()},
        )
    else:
        return JSONResponse(
            status_code=500,
            content={"detail": "服务器内部错误，请稍后重试。"},
        )
