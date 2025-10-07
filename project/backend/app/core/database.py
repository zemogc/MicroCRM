from sqlmodel import SQLModel, create_engine, Session
from .settings import get_settings

settings = get_settings()

# Build MySQL connection URL
if settings.database_url:
    # Use provided database URL (for production)
    DATABASE_URL = settings.database_url
else:
    # Use MySQL configuration from settings
    DATABASE_URL = f"mysql+pymysql://{settings.mysql_user}:{settings.mysql_password}@{settings.mysql_host}:{settings.mysql_port}/{settings.mysql_database}"

# Create engine
engine = create_engine(
    DATABASE_URL,
    echo=True,  # Set to False in production
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=300,    # Recycle connections every 5 minutes
)

def get_session():
    """Dependency to get database session"""
    with Session(engine) as session:
        yield session
