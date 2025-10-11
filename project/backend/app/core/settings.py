from functools import lru_cache
from pydantic import BaseModel
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

class Settings(BaseModel):
    secret_key: str = os.getenv("SECRET_KEY", "devsecret")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    
    # Database settings
    database_url: str = os.getenv("DATABASE_URL", "")  # Empty by default to use MySQL config
    mysql_host: str = os.getenv("MYSQL_HOST", "localhost")
    mysql_port: int = int(os.getenv("MYSQL_PORT", "3306"))
    mysql_user: str = os.getenv("MYSQL_USER", "root")
    mysql_password: str = os.getenv("MYSQL_PASSWORD", "root")
    mysql_database: str = os.getenv("MYSQL_DATABASE", "microcrm_db")
    
    cors_origins: list[str] = [o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")]
    rate_limit_auth_per_min: int = int(os.getenv("RATE_LIMIT_AUTH_PER_MIN", "5"))
    rate_limit_api_per_min: int = int(os.getenv("RATE_LIMIT_API_PER_MIN", "60"))

@lru_cache
def get_settings() -> Settings:
    return Settings()
