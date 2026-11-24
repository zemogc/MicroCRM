from sqlmodel import SQLModel, Field
from pydantic import field_validator
from typing import Optional
from datetime import datetime, timezone
from ..core.clock import utcnow

# Kanban flow: pending -> in_progress -> in_review -> completed
# 'overdue' is set automatically when due_date passes; 'cancelled' closes the task
TASK_STATUSES = ["pending", "in_progress", "overdue", "in_review", "completed", "cancelled"]


def _validate_status(v: Optional[str]) -> Optional[str]:
    if v is not None and v not in TASK_STATUSES:
        raise ValueError(f"El estado debe ser uno de: {', '.join(TASK_STATUSES)}")
    return v


def _clean_title(v: Optional[str]) -> Optional[str]:
    if v is None:
        return v
    if len(v.strip()) == 0:
        raise ValueError("El título de la tarea no puede estar vacío")
    return v.strip()


def _to_utc_naive(v: Optional[datetime]) -> Optional[datetime]:
    """Fechas con zona horaria se pasan a UTC sin zona, como se guardan (ver core.clock).

    Sin esto, "10:00-05:00" quedaba guardado como 10:00 UTC y la tarea vencía 5 horas antes.
    """
    if v is not None and v.tzinfo is not None:
        return v.astimezone(timezone.utc).replace(tzinfo=None)
    return v


class TaskBase(SQLModel):
    project_id: int = Field(foreign_key="projects.id", ondelete="CASCADE")
    title: str = Field(max_length=150)
    description: Optional[str] = Field(default=None, max_length=150)
    status: str = Field(default="pending", max_length=50)
    assigned_to: Optional[int] = Field(default=None, foreign_key="users.id", ondelete="SET NULL")
    due_date: Optional[datetime] = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, v):
        return _clean_title(v)

    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        return _validate_status(v)

    @field_validator("due_date")
    @classmethod
    def validate_due_date(cls, v):
        return _to_utc_naive(v)

class Task(TaskBase, table=True):
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=utcnow)


class TaskCreate(TaskBase):
    pass

class TaskUpdate(SQLModel):
    title: Optional[str] = Field(default=None, max_length=150)
    description: Optional[str] = Field(default=None, max_length=150)
    status: Optional[str] = Field(default=None, max_length=50)
    assigned_to: Optional[int] = None
    due_date: Optional[datetime] = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, v):
        return _clean_title(v)

    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        return _validate_status(v)

    @field_validator("due_date")
    @classmethod
    def validate_due_date(cls, v):
        return _to_utc_naive(v)

class TaskResponse(SQLModel):
    id: int
    project_id: int
    title: str
    description: Optional[str] = None
    status: str
    assigned_to: Optional[int] = None
    created_at: datetime
    due_date: Optional[datetime] = None
    # Include related information
    project_name: Optional[str] = None
    project_description: Optional[str] = None
    assigned_to_name: Optional[str] = None
    assigned_to_email: Optional[str] = None
