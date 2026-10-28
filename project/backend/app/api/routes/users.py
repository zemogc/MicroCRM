from fastapi import APIRouter, HTTPException, Query
from sqlmodel import select
from typing import Optional
from ...models.user import User, UserCreate, UserUpdate, UserResponse
from ...models.pagination import PaginatedResponse
from ...core.auth import CurrentUser, SessionDep
from ...core.cascade import delete_user_tree
from ...core.clock import utcnow
from ...core.permissions import ensure_self
from ...core.query import apply_ordering, count_rows
from ...core.security import hash_password

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/", response_model=PaginatedResponse[UserResponse])
def list_users(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=10, ge=1, le=100, description="Number of records to return"),
    order_by: str = Query(default="updated_at", description="Field to order by"),
    order_dir: str = Query(default="desc", description="Order direction (asc or desc)"),
    search: Optional[str] = Query(default=None, description="Search by name or email"),
    active: Optional[bool] = Query(default=None, description="Filter by active status"),
) -> PaginatedResponse[UserResponse]:
    """Directory of users (used to add collaborators to projects)"""
    statement = select(User)

    if search:
        search_filter = f"%{search}%"
        statement = statement.where(
            (User.name.like(search_filter)) | (User.email.like(search_filter))
        )

    if active is not None:
        statement = statement.where(User.active == active)

    total = count_rows(session, statement)
    # Never order by the password hash
    safe_order_by = order_by if order_by != "password" else "updated_at"
    statement = apply_ordering(statement, User, safe_order_by, order_dir, default="updated_at")
    users = session.exec(statement.offset(skip).limit(limit)).all()

    return PaginatedResponse(
        items=[UserResponse.model_validate(user) for user in users],
        total=total,
        skip=skip,
        limit=limit,
        has_more=(skip + limit) < total
    )

@router.post("/", response_model=UserResponse, status_code=201)
def create_user(payload: UserCreate, session: SessionDep, current_user: CurrentUser) -> UserResponse:
    """Create a new user account (e.g. to invite a teammate)"""
    existing_user = session.exec(select(User).where(User.email == payload.email)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already exists")

    user_data = payload.model_dump()
    user_data['password'] = hash_password(user_data['password'])

    user = User(**user_data)
    session.add(user)
    session.commit()
    session.refresh(user)
    return UserResponse.model_validate(user)

@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, session: SessionDep, current_user: CurrentUser) -> UserResponse:
    """Get user by ID"""
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse.model_validate(user)

@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, payload: UserUpdate, session: SessionDep, current_user: CurrentUser) -> UserResponse:
    """Update the current user's profile"""
    ensure_self(current_user, user_id)
    user = current_user

    if payload.email and payload.email != user.email:
        statement = select(User).where(User.email == payload.email, User.id != user_id)
        if session.exec(statement).first():
            raise HTTPException(status_code=400, detail="Email already exists")

    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user, key, value)
    user.updated_at = utcnow()

    session.add(user)
    session.commit()
    session.refresh(user)
    return UserResponse.model_validate(user)

@router.delete("/{user_id}", status_code=204)
def delete_user(user_id: int, session: SessionDep, current_user: CurrentUser):
    """Delete the current user's account, the projects they own and their memberships"""
    ensure_self(current_user, user_id)
    delete_user_tree(session, current_user)
    session.commit()
    return None
