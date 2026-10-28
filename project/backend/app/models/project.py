from sqlmodel import SQLModel, Field, Relationship
from pydantic import field_validator
from typing import Optional, TYPE_CHECKING
from datetime import datetime
from ..core.clock import utcnow

if TYPE_CHECKING:
    from .user import User


def _clean_name(v: Optional[str]) -> Optional[str]:
    if v is None:
        return v
    if len(v.strip()) == 0:
        raise ValueError("El nombre del proyecto no puede estar vacío")
    return v.strip()


class ProjectBase(SQLModel):
    name: str = Field(max_length=100)
    description: Optional[str] = Field(default=None, max_length=150)

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        return _clean_name(v)

class Project(ProjectBase, table=True):
    __tablename__ = "projects"

    id: Optional[int] = Field(default=None, primary_key=True)
    id_user: int = Field(foreign_key="users.id", ondelete="CASCADE")
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)

    # Relationships
    creator: Optional["User"] = Relationship(back_populates="created_projects")

class ProjectCreate(ProjectBase):
    """The creator is always the authenticated user (taken from the token)"""
    pass

class ProjectUpdate(SQLModel):
    name: Optional[str] = Field(default=None, max_length=100)
    description: Optional[str] = Field(default=None, max_length=150)

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        return _clean_name(v)

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
