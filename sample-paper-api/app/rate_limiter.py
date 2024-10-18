import time
from fastapi import HTTPException, Request
from functools import wraps
from .config import redis_client as r


async def is_rate_limited(ip_address: str, limit: int, time_window: int) -> bool:
    current_time = int(time.time())
    key = f"rate_limit:{ip_address}"
    await r.zadd(key, {current_time: current_time})
    
    ttl = await r.ttl(key)
    if ttl == -1:
        await r.expire(key, time_window)

    request_count = await r.zcount(key, current_time - time_window, current_time)
    return request_count > limit

def rate_limit(limit: int, time_window: int):
    def decorator(func):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            ip_address = request.client.host

            if await is_rate_limited(ip_address, limit, time_window):
                raise HTTPException(status_code=429, detail="Too many requests. Try again later.")
            
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator