from sqlmodel import SQLModel, Field, Relationship
from pydantic import field_validator
from typing import Optional
from datetime import datetime

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
        if not v or len(v.strip()) == 0:
            raise ValueError("Task title cannot be empty")
        if len(v) > 150:
            raise ValueError("Task title must be 150 characters or less")
        return v.strip()

    @field_validator("description")
    @classmethod
    def validate_description(cls, v):
        if v and len(v) > 150:
            raise ValueError("Task description must be 150 characters or less")
        return v

    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        valid_statuses = ["pending", "in_progress", "overdue", "in_review", "completed", "cancelled"]
        if v not in valid_statuses:
            raise ValueError(f"Status must be one of: {', '.join(valid_statuses)}")
        return v

class Task(TaskBase, table=True):
    __tablename__ = "tasks"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    

class TaskCreate(TaskBase):
    pass

class TaskUpdate(SQLModel):
    title: Optional[str] = Field(default=None, max_length=150)
    description: Optional[str] = Field(default=None, max_length=150)
    status: Optional[str] = Field(default=None, max_length=50)
    assigned_to: Optional[int] = None
    due_date: Optional[datetime] = None
    
    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        if v is not None:  # Solo validar si se proporciona un status
            valid_statuses = ["pending", "in_progress", "overdue", "in_review", "completed", "cancelled"]
            if v not in valid_statuses:
                raise ValueError(f"Status must be one of: {', '.join(valid_statuses)}")
        return v

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

    class Config:
        from_attributes = True
