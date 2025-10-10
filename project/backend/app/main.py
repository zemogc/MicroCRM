from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from contextlib import asynccontextmanager
from .core.settings import get_settings
from .core.exceptions import (
    http_exception_handler,
    validation_exception_handler,
    sqlalchemy_exception_handler,
    general_exception_handler
)
from .core.scheduler import start_scheduler, stop_scheduler
from .api.routes import auth, users, projects, tasks, roles, project_members


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan events"""
    # Startup
    await start_scheduler()
    yield
    # Shutdown
    await stop_scheduler()


app = FastAPI(
    title="Micro CRM API", 
    version="0.1.0",
    description="API para gestión de proyectos y tareas - CRM de proyectos",
    lifespan=lifespan
)

settings = get_settings()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

@app.get("/health")
def health():
    return {"status": "ok", "message": "Micro CRM API is running"}

@app.get("/")
def root():
    return {
        "message": "Micro CRM API - Gestión de Proyectos",
        "version": "0.1.0",
        "endpoints": {
            "auth": "/api/auth",
            "users": "/api/users",
            "projects": "/api/projects", 
            "tasks": "/api/tasks",
            "roles": "/api/roles",
            "project_members": "/api/project-members"
        }
    }

# Registro de routers
app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(projects.router, prefix="/api")
app.include_router(tasks.router, prefix="/api")
app.include_router(roles.router, prefix="/api")
app.include_router(project_members.router, prefix="/api")
