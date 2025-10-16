from sqlmodel import SQLModel, Field, Relationship
from pydantic import field_validator
from typing import Optional
from datetime import datetime

class ProjectBase(SQLModel):
    name: str = Field(max_length=100)
    description: Optional[str] = Field(default=None, max_length=150)
    id_user: int = Field(foreign_key="users.id", ondelete="CASCADE")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError("Project name cannot be empty")
        if len(v) > 100:
            raise ValueError("Project name must be 100 characters or less")
        return v.strip()

    @field_validator("description")
    @classmethod
    def validate_description(cls, v):
        if v and len(v) > 150:
            raise ValueError("Project description must be 150 characters or less")
        return v

class Project(ProjectBase, table=True):
    __tablename__ = "projects"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    creator: Optional["User"] = Relationship(back_populates="created_projects")

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(SQLModel):
    name: Optional[str] = Field(default=None, max_length=100)
    description: Optional[str] = Field(default=None, max_length=150)

class ProjectResponse(SQLModel):
    id: int
    name: str
    description: Optional[str] = None
    id_user: int
    created_at: datetime
    updated_at: datetime
    # Include creator information
    creator_name: Optional[str] = None
    creator_email: Optional[str] = None

    class Config:
        from_attributes = True
