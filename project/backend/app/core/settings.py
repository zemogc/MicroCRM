from functools import lru_cache
from pydantic import BaseModel
import os

class Settings(BaseModel):
    secret_key: str = os.getenv("SECRET_KEY", "devsecret")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./app.db")
    cors_origins: list[str] = [o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")]
    rate_limit_auth_per_min: int = int(os.getenv("RATE_LIMIT_AUTH_PER_MIN", "5"))
    rate_limit_api_per_min: int = int(os.getenv("RATE_LIMIT_API_PER_MIN", "60"))

@lru_cache
def get_settings() -> Settings:
    return Settings()
