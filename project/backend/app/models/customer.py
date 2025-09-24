from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import datetime
import re

PHONE_RE = re.compile(r"^[0-9\s\-\+]{10,15}$")

class CustomerBase(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    notes: Optional[str] = None

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v):
        if v is None or v == "":
            return v
        if not PHONE_RE.match(v):
            raise ValueError("Phone must be 10-15 digits (may include +, -, spaces)")
        return v

class CustomerCreate(CustomerBase):
    pass

class Customer(CustomerBase):
    id: int
    created_at: datetime
    updated_at: datetime
