from pydantic import BaseModel, field_validator
from typing import Optional, Literal
from datetime import datetime

Status = Literal["prospecto", "en_curso", "pausado", "cerrado"]

class ProjectBase(BaseModel):
    customer_id: int
    name: str
    status: Status = "prospecto"
    budget: Optional[float] = None
    start_date: Optional[datetime] = None
    notes: Optional[str] = None

    @field_validator("budget")
    @classmethod
    def positive_budget(cls, v):
        if v is not None and v < 0:
            raise ValueError("Budget must be positive")
        return v

class ProjectCreate(ProjectBase):
    pass

class Project(ProjectBase):
    id: int
    created_at: datetime
    updated_at: datetime
