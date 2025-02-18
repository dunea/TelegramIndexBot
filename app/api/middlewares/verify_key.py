from fastapi import Header


async def verify_token(x_token: str = Header(...)):
    """
    验证token
    如果token无效，则抛出401错误
    如果token有效，则返回token绑定的用户id
    @param x_token: 请求头中的token
    @return: token绑定的用户id
    """
    try:
        auth = user_svc.verify_auth_token(x_token)
        if auth is None:
            raise HTTPException(status_code=401, detail="无效的令牌")
        if auth.expire_at < datetime.now():
            raise HTTPException(status_code=401, detail="过期的令牌")
    except ValueError as e:
        raise HTTPException(status_code=401, detail="无效的令牌")
    return auth.user_id
