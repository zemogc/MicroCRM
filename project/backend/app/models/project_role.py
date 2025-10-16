from sqlmodel import SQLModel, Field, Relationship
from pydantic import field_validator
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from .project import Project
    from .project_member import ProjectMember

class ProjectRoleBase(SQLModel):
    name: str = Field(max_length=50, index=True)
    description: Optional[str] = Field(default=None, max_length=150)
    project_id: int = Field(foreign_key="projects.id", ondelete="CASCADE")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError("Role name cannot be empty")
        if len(v) > 50:
            raise ValueError("Role name must be 50 characters or less")
        return v.strip()

class ProjectRole(ProjectRoleBase, table=True):
    __tablename__ = "project_roles"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Relationships
    project: Optional["Project"] = Relationship()
    project_members: List["ProjectMember"] = Relationship(back_populates="project_role")

class ProjectRoleCreate(ProjectRoleBase):
    pass

class ProjectRoleUpdate(SQLModel):
    name: Optional[str] = Field(default=None, max_length=50)
    description: Optional[str] = Field(default=None, max_length=150)

class ProjectRoleResponse(SQLModel):
    id: int
    name: str
    description: Optional[str] = None
    project_id: int
    # Include related data
    project_name: Optional[str] = None

    class Config:
        from_attributes = True
