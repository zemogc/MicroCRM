from sqlmodel import SQLModel, Field
from pydantic import EmailStr, field_validator
from typing import Optional
from datetime import datetime
from ..core.clock import utcnow

# Sales pipeline: a lead becomes an active client; inactive keeps the history
CLIENT_STATUSES = ["lead", "active", "inactive"]


def _validate_status(v: Optional[str]) -> Optional[str]:
    if v is not None and v not in CLIENT_STATUSES:
        raise ValueError(f"El estado debe ser uno de: {', '.join(CLIENT_STATUSES)}")
    return v


def _clean_name(v: Optional[str]) -> Optional[str]:
    if v is None:
        return v
    if len(v.strip()) == 0:
        raise ValueError("El nombre del cliente no puede estar vacío")
    return v.strip()


def _empty_to_none(v):
    # Forms send "" for untouched optional fields
    return None if isinstance(v, str) and v.strip() == "" else v


class ClientBase(SQLModel):
    name: str = Field(max_length=100)
    company: Optional[str] = Field(default=None, max_length=100)
    email: Optional[EmailStr] = Field(default=None, max_length=150)
    phone: Optional[str] = Field(default=None, max_length=30)
    status: str = Field(default="lead", max_length=20)
    notes: Optional[str] = Field(default=None, max_length=500)

    @field_validator("company", "email", "phone", "notes", mode="before")
    @classmethod
    def empty_strings_are_null(cls, v):
        return _empty_to_none(v)

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        return _clean_name(v)

    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        return _validate_status(v)

class Client(ClientBase, table=True):
    __tablename__ = "clients"

    id: Optional[int] = Field(default=None, primary_key=True)
    owner_id: int = Field(foreign_key="users.id", ondelete="CASCADE", index=True)
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)

class ClientCreate(ClientBase):
    pass

class ClientUpdate(SQLModel):
    name: Optional[str] = Field(default=None, max_length=100)
    company: Optional[str] = Field(default=None, max_length=100)
    email: Optional[EmailStr] = Field(default=None, max_length=150)
    phone: Optional[str] = Field(default=None, max_length=30)
    status: Optional[str] = Field(default=None, max_length=20)
    notes: Optional[str] = Field(default=None, max_length=500)

    @field_validator("company", "email", "phone", "notes", mode="before")
    @classmethod
    def empty_strings_are_null(cls, v):
        return _empty_to_none(v)

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        return _clean_name(v)

    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        return _validate_status(v)

class ClientResponse(SQLModel):
    id: int
    name: str
    company: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    status: str
    notes: Optional[str] = None
    owner_id: int
    created_at: datetime
    updated_at: datetime
