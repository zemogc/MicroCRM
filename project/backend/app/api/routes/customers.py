from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone
from typing import List
from ...models.customer import Customer, CustomerCreate

router = APIRouter(prefix="/customers", tags=["customers"])

# In-memory store (Semana 3)
CUSTOMERS: list[Customer] = []
_COUNTER = 1

@router.get("/", response_model=List[Customer])
def list_customers() -> List[Customer]:
    return sorted(CUSTOMERS, key=lambda c: c.updated_at, reverse=True)

@router.post("/", response_model=Customer, status_code=201)
def create_customer(payload: CustomerCreate) -> Customer:
    global _COUNTER
    now = datetime.now(timezone.utc)
    c = Customer(id=_COUNTER, created_at=now, updated_at=now, **payload.model_dump())
    _COUNTER += 1
    CUSTOMERS.append(c)
    return c

@router.get("/{customer_id}", response_model=Customer)
def get_customer(customer_id: int) -> Customer:
    for c in CUSTOMERS:
        if c.id == customer_id:
            return c
    raise HTTPException(status_code=404, detail="Customer not found")
