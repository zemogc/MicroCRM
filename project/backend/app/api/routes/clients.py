from fastapi import APIRouter, HTTPException, Query
from sqlmodel import Session, select
from typing import Optional
from ...models.client import Client, ClientCreate, ClientUpdate, ClientResponse
from ...models.user import User
from ...models.pagination import PaginatedResponse
from ...core.auth import CurrentUser, SessionDep
from ...core.clock import utcnow
from ...core.query import apply_ordering, count_rows

router = APIRouter(prefix="/clients", tags=["clients"])

def get_own_client(session: Session, client_id: int, current_user: User) -> Client:
    """Each user manages their own client portfolio; others get 404"""
    client = session.get(Client, client_id)
    if not client or client.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Client not found")
    return client

@router.get("/", response_model=PaginatedResponse[ClientResponse])
def list_clients(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=10, ge=1, le=100, description="Number of records to return"),
    order_by: str = Query(default="updated_at", description="Field to order by"),
    order_dir: str = Query(default="desc", description="Order direction (asc or desc)"),
    search: Optional[str] = Query(default=None, description="Search by name, company or email"),
    status: Optional[str] = Query(default=None, description="Filter by status (lead, active, inactive)"),
) -> PaginatedResponse[ClientResponse]:
    """Clients of the current user with filtering and ordering"""
    statement = select(Client).where(Client.owner_id == current_user.id)

    if search:
        search_filter = f"%{search}%"
        statement = statement.where(
            (Client.name.like(search_filter))
            | (Client.company.like(search_filter))
            | (Client.email.like(search_filter))
        )

    if status:
        statement = statement.where(Client.status == status)

    total = count_rows(session, statement)
    statement = apply_ordering(statement, Client, order_by, order_dir, default="updated_at")
    clients = session.exec(statement.offset(skip).limit(limit)).all()

    return PaginatedResponse(
        items=[ClientResponse.model_validate(client) for client in clients],
        total=total,
        skip=skip,
        limit=limit,
        has_more=(skip + limit) < total
    )

@router.post("/", response_model=ClientResponse, status_code=201)
def create_client(payload: ClientCreate, session: SessionDep, current_user: CurrentUser) -> ClientResponse:
    """Create a client in the current user's portfolio"""
    client = Client(**payload.model_dump(), owner_id=current_user.id)
    session.add(client)
    session.commit()
    session.refresh(client)
    return ClientResponse.model_validate(client)

@router.get("/{client_id}", response_model=ClientResponse)
def get_client(client_id: int, session: SessionDep, current_user: CurrentUser) -> ClientResponse:
    """Get client by ID"""
    return ClientResponse.model_validate(get_own_client(session, client_id, current_user))

@router.put("/{client_id}", response_model=ClientResponse)
def update_client(client_id: int, payload: ClientUpdate, session: SessionDep, current_user: CurrentUser) -> ClientResponse:
    """Update client by ID"""
    client = get_own_client(session, client_id, current_user)

    update_data = payload.model_dump(exclude_unset=True)
    if update_data.get("name") is None:
        update_data.pop("name", None)  # name is required, null means "unchanged"
    for key, value in update_data.items():
        setattr(client, key, value)
    client.updated_at = utcnow()

    session.add(client)
    session.commit()
    session.refresh(client)
    return ClientResponse.model_validate(client)

@router.delete("/{client_id}", status_code=204)
def delete_client(client_id: int, session: SessionDep, current_user: CurrentUser):
    """Delete client by ID"""
    client = get_own_client(session, client_id, current_user)
    session.delete(client)
    session.commit()
    return None
