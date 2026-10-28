from sqlalchemy import event, inspect, text
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


# Columns added after the first release: create_all does not alter existing tables,
# so they are added here when missing (table, column, DDL type, MySQL foreign key)
COLUMN_UPGRADES = [
    ("projects", "client_id", "INTEGER NULL",
     "FOREIGN KEY (client_id) REFERENCES clients (id) ON DELETE SET NULL"),
]


def upgrade_schema() -> None:
    """Add missing nullable columns to tables created by older versions (idempotent)"""
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    with engine.begin() as connection:
        for table, column, ddl, foreign_key in COLUMN_UPGRADES:
            if table not in tables:
                continue
            existing = {c["name"] for c in inspector.get_columns(table)}
            if column in existing:
                continue
            connection.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {ddl}"))
            if not is_sqlite and foreign_key:
                # SQLite cannot add constraints to an existing table; the app keeps it consistent
                connection.execute(text(f"ALTER TABLE {table} ADD {foreign_key}"))


def init_db() -> None:
    """Create all tables that do not exist yet and apply column upgrades"""
    from .. import models  # noqa: F401  (registers the tables in the metadata)
    SQLModel.metadata.create_all(engine)
    upgrade_schema()


def get_session():
    """Dependency to get database session"""
    with Session(engine) as session:
        yield session
