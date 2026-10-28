from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException
from contextlib import asynccontextmanager
from .core.settings import get_settings
from .core.database import init_db
from .core.exceptions import (
    http_exception_handler,
    validation_exception_handler,
    sqlalchemy_exception_handler,
    general_exception_handler
)
from .core.scheduler import start_scheduler, stop_scheduler
from .api.routes import auth, users, projects, tasks, project_members, project_roles, clients, dashboard

API_VERSION = "1.0.0"

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan events"""
    # Startup
    if settings.auto_create_tables:
        init_db()
    if settings.enable_scheduler:
        await start_scheduler()
    yield
    # Shutdown
    await stop_scheduler()


app = FastAPI(
    title="Micro CRM API",
    version=API_VERSION,
    description="API para gestión de proyectos y tareas - CRM de proyectos",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "Accept", "Origin", "X-Requested-With"],
    expose_headers=["Content-Length", "X-Total-Count"],
    max_age=600,  # Cache preflight requests for 10 minutes
)

# Exception handlers
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

@app.get("/health", tags=["system"])
def health():
    return {"status": "ok", "message": "Micro CRM API is running"}

@app.get("/", tags=["system"])
def root():
    return {
        "message": "Micro CRM API - Gestión de Proyectos",
        "version": API_VERSION,
        "docs": "/api/docs",
        "endpoints": {
            "auth": "/api/auth",
            "users": "/api/users",
            "projects": "/api/projects",
            "tasks": "/api/tasks",
            "project_members": "/api/project-members",
            "project_roles": "/api/project-roles",
            "clients": "/api/clients",
            "dashboard": "/api/dashboard"
        }
    }

# Registro de routers
app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(projects.router, prefix="/api")
app.include_router(tasks.router, prefix="/api")
app.include_router(project_members.router, prefix="/api")
app.include_router(project_roles.router, prefix="/api")
app.include_router(clients.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")
