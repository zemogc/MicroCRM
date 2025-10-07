from sqlmodel import SQLModel, Field
from pydantic import field_validator
from typing import Optional

class RoleBase(SQLModel):
    name: str = Field(max_length=50, unique=True, index=True)
    description: Optional[str] = Field(default=None, max_length=150)

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError("Role name cannot be empty")
        if len(v) > 50:
            raise ValueError("Role name must be 50 characters or less")
        return v.strip()

class Role(RoleBase, table=True):
    __tablename__ = "roles"
    
    id: Optional[int] = Field(default=None, primary_key=True)

class RoleCreate(RoleBase):
    pass

class RoleUpdate(SQLModel):
    name: Optional[str] = Field(default=None, max_length=50)
    description: Optional[str] = Field(default=None, max_length=150)

class RoleResponse(SQLModel):
    id: int
    name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True
