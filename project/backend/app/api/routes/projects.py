from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone
from typing import List
from ...models.project import Project, ProjectCreate
from .customers import CUSTOMERS

router = APIRouter(prefix="/projects", tags=["projects"])

PROJECTS: list[Project] = []
_COUNTER = 1

@router.get("/", response_model=List[Project])
def list_projects() -> List[Project]:
    return sorted(PROJECTS, key=lambda p: p.updated_at, reverse=True)

@router.post("/", response_model=Project, status_code=201)
def create_project(payload: ProjectCreate) -> Project:
    global _COUNTER
    # Validar que el cliente exista (FK)
    if not any(c.id == payload.customer_id for c in CUSTOMERS):
        raise HTTPException(status_code=400, detail="customer_id does not exist")
    now = datetime.now(timezone.utc)
    p = Project(id=_COUNTER, created_at=now, updated_at=now, **payload.model_dump())
    _COUNTER += 1
    PROJECTS.append(p)
    return p
