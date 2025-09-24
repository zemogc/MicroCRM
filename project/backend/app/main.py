from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.settings import get_settings
from .api.routes import customers, projects  # <-- importa routers

app = FastAPI(title="Micro CRM API", version="0.1.0")

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
    return {"status": "ok"}

# Registro de routers
app.include_router(customers.router, prefix="/api")
app.include_router(projects.router, prefix="/api")
