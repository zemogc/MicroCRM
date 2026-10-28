from sqlmodel import SQLModel, Field, Relationship
from pydantic import EmailStr, field_validator
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
import re
from ..core.clock import utcnow

if TYPE_CHECKING:
    from .project import Project


def validate_password_strength(v: str) -> str:
    """Min 8 chars, at least 1 uppercase, 1 lowercase, 1 number. Allowed specials: @$!%*?&._-#"""
    if len(v) < 8:
        raise ValueError("La contraseña debe tener al menos 8 caracteres")
    if not re.search(r'[a-z]', v):
        raise ValueError("La contraseña debe contener al menos una letra minúscula")
    if not re.search(r'[A-Z]', v):
        raise ValueError("La contraseña debe contener al menos una letra MAYÚSCULA")
    if not re.search(r'\d', v):
        raise ValueError("La contraseña debe contener al menos un número")
    if not re.match(r'^[a-zA-Z\d@$!%*?&._\-#]+$', v):
        raise ValueError("La contraseña solo puede contener letras, números y los caracteres especiales: @$!%*?&._-#")
    return v


def _clean_name(v: Optional[str]) -> Optional[str]:
    if v is None:
        return v
    if len(v.strip()) == 0:
        raise ValueError("El nombre no puede estar vacío")
    return v.strip()


class UserBase(SQLModel):
    name: str = Field(max_length=100)
    email: EmailStr = Field(max_length=150, unique=True, index=True)
    password: str = Field(max_length=255)
    active: bool = Field(default=True)

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        return _clean_name(v)

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        return validate_password_strength(v)

class User(UserBase, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)

    # Relationships
    created_projects: List["Project"] = Relationship(
        back_populates="creator",
        sa_relationship_kwargs={"passive_deletes": True}
    )

class UserCreate(UserBase):
    pass

class UserUpdate(SQLModel):
    name: Optional[str] = Field(default=None, max_length=100)
    email: Optional[EmailStr] = Field(default=None, max_length=150)
    active: Optional[bool] = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        return _clean_name(v)

class UserResponse(SQLModel):
    id: int
    name: str
    email: str
    active: bool
    created_at: datetime
    updated_at: datetime

class UserRegister(SQLModel):
    name: str = Field(max_length=100)
    email: EmailStr = Field(max_length=150)
    password: str = Field(max_length=255)

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        return _clean_name(v)

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        return validate_password_strength(v)

class UserLogin(SQLModel):
    email: EmailStr
    password: str

class UserLoginResponse(SQLModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
