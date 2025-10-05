from datetime import datetime, timedelta, timezone
from typing import Optional, Any
from jose import jwt, JWTError
from passlib.context import CryptContext
from .settings import get_settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ALGO = "HS256"

def hash_password(p: str) -> str:
    return pwd_context.hash(p)

def verify_password(p: str, hashed: str) -> bool:
    return pwd_context.verify(p, hashed)

def create_access_token(data: dict[str, Any], expires_minutes: int) -> str:
    settings = get_settings()
    to_encode = data.copy()
    expire = datetime.now(tz=timezone.utc) + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm=ALGO)

def decode_token(token: str) -> Optional[dict[str, Any]]:
    try:
        payload = jwt.decode(token, get_settings().secret_key, algorithms=[ALGO])
        return payload
    except JWTError:
        return None
