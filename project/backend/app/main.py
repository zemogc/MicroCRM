from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.settings import get_settings
from .api.routes import users, projects, tasks, roles, project_members

app = FastAPI(
    title="Micro CRM API", 
    version="0.1.0",
    description="API para gestión de proyectos y tareas - CRM de proyectos"
)

settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok", "message": "Micro CRM API is running"}

@app.get("/")
def root():
    return {
        "message": "Micro CRM API - Gestión de Proyectos",
        "version": "0.1.0",
        "endpoints": {
            "users": "/api/users",
            "projects": "/api/projects", 
            "tasks": "/api/tasks",
            "roles": "/api/roles",
            "project_members": "/api/project-members"
        }
    }

# Registro de routers
app.include_router(users.router, prefix="/api")
app.include_router(projects.router, prefix="/api")
app.include_router(tasks.router, prefix="/api")
app.include_router(roles.router, prefix="/api")
app.include_router(project_members.router, prefix="/api")
