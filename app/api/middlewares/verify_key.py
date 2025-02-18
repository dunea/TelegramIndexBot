from fastapi import Header, HTTPException

from app.core.settings import settings


async def verify_key(api_key: str = Header(...)):
    """
    验证token
    如果token无效，则抛出401错误
    如果token有效，则返回token绑定的用户id
    @param x_token: 请求头中的token
    @return: token绑定的用户id
    """
    try:
        if not api_key:
            raise HTTPException(status_code=401, detail="无效的令牌")
        if api_key != settings.API_KEY:
            raise HTTPException(status_code=401, detail="无效的令牌")
    except ValueError as e:
        raise HTTPException(status_code=401, detail="无效的令牌")
    return api_key
