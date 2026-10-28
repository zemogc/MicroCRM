from sqlalchemy import event
from sqlmodel import SQLModel, create_engine, Session
from .settings import get_settings

settings = get_settings()

# Build connection URL
if settings.database_url:
    # Use provided database URL (SQLite for development/tests, or any SQLAlchemy URL)
    DATABASE_URL = settings.database_url
else:
    # Use MySQL configuration from settings
    DATABASE_URL = f"mysql+pymysql://{settings.mysql_user}:{settings.mysql_password}@{settings.mysql_host}:{settings.mysql_port}/{settings.mysql_database}"

is_sqlite = DATABASE_URL.startswith("sqlite")

# Create engine
engine = create_engine(
    DATABASE_URL,
    echo=settings.db_echo,
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=300,    # Recycle connections every 5 minutes
    connect_args={"check_same_thread": False} if is_sqlite else {},
)

if is_sqlite:
    @event.listens_for(engine, "connect")
    def _enable_sqlite_foreign_keys(dbapi_connection, _):
        # SQLite ignores foreign keys unless explicitly enabled per connection
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


def init_db() -> None:
    """Create all tables that do not exist yet"""
    from .. import models  # noqa: F401  (registers the tables in the metadata)
    SQLModel.metadata.create_all(engine)


def get_session():
    """Dependency to get database session"""
    with Session(engine) as session:
        yield session
