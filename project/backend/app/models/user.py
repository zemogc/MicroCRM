from sqlmodel import SQLModel, Field, Relationship
from pydantic import EmailStr, field_validator
from typing import Optional, List
from datetime import datetime
import re

PASSWORD_RE = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d@$!%*?&]{8,}$")

class UserBase(SQLModel):
    name: str = Field(max_length=100)
    email: EmailStr = Field(max_length=150, unique=True, index=True)
    password: str = Field(max_length=255)
    active: bool = Field(default=True)

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        if not PASSWORD_RE.match(v):
            raise ValueError("Password must be at least 8 characters with uppercase, lowercase, and number")
        return v

class User(UserBase, table=True):
    __tablename__ = "users"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    created_projects: List["Project"] = Relationship(back_populates="creator")

class UserCreate(UserBase):
    pass

class UserUpdate(SQLModel):
    name: Optional[str] = Field(default=None, max_length=100)
    email: Optional[EmailStr] = Field(default=None, max_length=150)
    active: Optional[bool] = None

class UserResponse(SQLModel):
    id: int
    name: str
    email: str
    active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UserRegister(SQLModel):
    name: str = Field(max_length=100)
    email: EmailStr = Field(max_length=150)
    password: str = Field(max_length=255)

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        if not PASSWORD_RE.match(v):
            raise ValueError("Password must be at least 8 characters with uppercase, lowercase, and number")
        return v

class UserLogin(SQLModel):
    email: EmailStr
    password: str

class UserLoginResponse(SQLModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
