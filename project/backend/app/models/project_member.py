from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime

class ProjectMemberBase(SQLModel):
    project_id: int = Field(foreign_key="projects.id", ondelete="CASCADE")
    user_id: int = Field(foreign_key="users.id", ondelete="CASCADE")
    role_id: int = Field(foreign_key="roles.id", ondelete="RESTRICT")
    added_by: Optional[int] = Field(default=None, foreign_key="users.id", ondelete="SET NULL")

class ProjectMember(ProjectMemberBase, table=True):
    __tablename__ = "project_members"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    

class ProjectMemberCreate(ProjectMemberBase):
    pass

class ProjectMemberUpdate(SQLModel):
    role_id: int

class ProjectMemberResponse(SQLModel):
    id: int
    project_id: int
    user_id: int
    role_id: int
    added_by: Optional[int] = None
    created_at: datetime
    # Include related data
    user_name: Optional[str] = None
    role_name: Optional[str] = None
    added_by_name: Optional[str] = None

    class Config:
        from_attributes = True
