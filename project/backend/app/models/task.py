from sqlmodel import SQLModel, Field, Relationship
from pydantic import field_validator
from typing import Optional
from datetime import datetime

class TaskBase(SQLModel):
    project_id: int = Field(foreign_key="projects.id")
    title: str = Field(max_length=150)
    description: Optional[str] = Field(default=None, max_length=150)
    status: str = Field(default="pending", max_length=50)
    assigned_to: Optional[int] = Field(default=None, foreign_key="users.id")
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
        valid_statuses = ["pending", "in_progress", "completed", "cancelled"]
        if v not in valid_statuses:
            raise ValueError(f"Status must be one of: {', '.join(valid_statuses)}")
        return v

class Task(TaskBase, table=True):
    __tablename__ = "tasks"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    crated_by: int = Field(foreign_key="users.id")  # Note: keeping the typo from the diagram
    created_at: datetime = Field(default_factory=datetime.utcnow)
    

class TaskCreate(TaskBase):
    pass

class TaskUpdate(SQLModel):
    title: Optional[str] = Field(default=None, max_length=150)
    description: Optional[str] = Field(default=None, max_length=150)
    status: Optional[str] = Field(default=None, max_length=50)
    assigned_to: Optional[int] = None
    due_date: Optional[datetime] = None

class TaskResponse(SQLModel):
    id: int
    project_id: int
    title: str
    description: Optional[str] = None
    status: str
    crated_by: int
    assigned_to: Optional[int] = None
    created_at: datetime
    due_date: Optional[datetime] = None
    # Include related information
    project_name: Optional[str] = None
    assigned_to_email: Optional[str] = None
    created_by_email: Optional[str] = None

    class Config:
        from_attributes = True
