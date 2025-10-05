import time
from fastapi import Request, HTTPException

# Estructuras simples en memoria: {key: [timestamps]}
AUTH_BUCKET: dict[str, list[float]] = {}
API_BUCKET: dict[str, list[float]] = {}

def _allow(bucket: dict, key: str, per_minute: int):
    now = time.time()
    window = 60.0
    arr = bucket.get(key, [])
    arr = [t for t in arr if now - t < window]
    if len(arr) >= per_minute:
        raise HTTPException(status_code=429, detail="Too Many Requests")
    arr.append(now)
    bucket[key] = arr

async def rate_limit_auth(request: Request, per_minute: int):
    ip = request.client.host if request.client else "unknown"
    _allow(AUTH_BUCKET, ip, per_minute)

async def rate_limit_api(request: Request, per_minute: int, token_sub: str | None):
    key = token_sub or (request.client.host if request.client else "unknown")
    _allow(API_BUCKET, key, per_minute)