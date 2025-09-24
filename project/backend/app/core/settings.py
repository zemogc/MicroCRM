from functools import lru_cache
from pydantic import BaseModel

class Settings(BaseModel):
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

@lru_cache
def get_settings() -> Settings:
    return Settings()
