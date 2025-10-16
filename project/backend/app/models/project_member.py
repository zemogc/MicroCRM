from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from .user import User
    from .project_role import ProjectRole
    from .project import Project

class ProjectMemberBase(SQLModel):
    project_id: int = Field(foreign_key="projects.id", ondelete="CASCADE")
    user_id: int = Field(foreign_key="users.id", ondelete="CASCADE")
    project_role_id: int = Field(foreign_key="project_roles.id", ondelete="RESTRICT")

class ProjectMember(ProjectMemberBase, table=True):
    __tablename__ = "project_members"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    project: Optional["Project"] = Relationship()
    user: Optional["User"] = Relationship()
    project_role: Optional["ProjectRole"] = Relationship(back_populates="project_members")

class ProjectMemberCreate(ProjectMemberBase):
    pass

class ProjectMemberUpdate(SQLModel):
    project_role_id: int

class ProjectMemberResponse(SQLModel):
    id: int
    project_id: int
    user_id: int
    project_role_id: int
    created_at: datetime
    # Include related data
    project_name: Optional[str] = None
    user_name: Optional[str] = None
    user_email: Optional[str] = None
    role_name: Optional[str] = None
    role_description: Optional[str] = None

    class Config:
        from_attributes = True
