import time
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse

# Estructuras simples en memoria: {key: [timestamps]}
AUTH_BUCKET: dict[str, list[float]] = {}
API_BUCKET: dict[str, list[float]] = {}

def _allow(bucket: dict, key: str, per_minute: int):
    now = time.time()
    window = 60.0
    arr = bucket.get(key, [])
    arr = [t for t in arr if now - t < window]
    
    if len(arr) >= per_minute:
        # Calculate time until oldest request expires
        oldest_request = min(arr)
        retry_after = int(window - (now - oldest_request)) + 1
        
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Too many requests. Please try again in {retry_after} seconds.",
            headers={"Retry-After": str(retry_after)}
        )
    
    arr.append(now)
    bucket[key] = arr

async def rate_limit_auth(request: Request, per_minute: int):
    ip = request.client.host if request.client else "unknown"
    _allow(AUTH_BUCKET, ip, per_minute)

async def rate_limit_api(request: Request, per_minute: int, token_sub: str | None = None):
    key = token_sub or (request.client.host if request.client else "unknown")
    _allow(API_BUCKET, key, per_minute)