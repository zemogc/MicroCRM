from fastapi import APIRouter, HTTPException, Depends, Request, Query
from sqlmodel import Session, select, func, col
from typing import List, Optional
from ...models.user import User, UserCreate, UserUpdate, UserResponse
from ...models.pagination import PaginatedResponse
from ...core.database import get_session
from ...core.security import hash_password
from ...core.settings import get_settings
from ...core.auth import get_current_active_user
from ...core.rate_limit import rate_limit_api

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/", response_model=PaginatedResponse[UserResponse])
async def list_users(
    request: Request,
    session: Session = Depends(get_session),
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=10, ge=1, le=100, description="Number of records to return"),
    order_by: str = Query(default="updated_at", description="Field to order by"),
    order_dir: str = Query(default="desc", description="Order direction (asc or desc)"),
    search: Optional[str] = Query(default=None, description="Search by name or email"),
    active: Optional[bool] = Query(default=None, description="Filter by active status"),
    current_user: User = Depends(get_current_active_user)
) -> PaginatedResponse[UserResponse]:
    """Get paginated list of users with filtering and ordering"""
    settings = get_settings()
    await rate_limit_api(request, settings.rate_limit_api_per_min, str(current_user.id))
    
    # Base query
    statement = select(User)
    
    # Apply filters
    if search:
        search_filter = f"%{search}%"
        statement = statement.where(
            (User.name.like(search_filter)) | (User.email.like(search_filter))
        )
    
    if active is not None:
        statement = statement.where(User.active == active)
    
    # Get total count
    count_statement = select(func.count()).select_from(statement.subquery())
    total = session.exec(count_statement).one()
    
    # Apply ordering
    order_column = getattr(User, order_by, User.updated_at)
    if order_dir.lower() == "asc":
        statement = statement.order_by(col(order_column).asc())
    else:
        statement = statement.order_by(col(order_column).desc())
    
    # Apply pagination
    statement = statement.offset(skip).limit(limit)
    
    # Execute query
    users = session.exec(statement).all()
    
    return PaginatedResponse(
        items=[UserResponse.model_validate(user) for user in users],
        total=total,
        skip=skip,
        limit=limit,
        has_more=(skip + limit) < total
    )

@router.post("/", response_model=UserResponse, status_code=201)
def create_user(payload: UserCreate, session: Session = Depends(get_session)) -> UserResponse:
    """Create a new user"""
    # Check if email already exists
    statement = select(User).where(User.email == payload.email)
    existing_user = session.exec(statement).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already exists")
    
    # Hash password before saving
    user_data = payload.model_dump()
    user_data['password'] = hash_password(user_data['password'])
    
    # Create new user
    user = User(**user_data)
    session.add(user)
    session.commit()
    session.refresh(user)
    return UserResponse.model_validate(user)

@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, session: Session = Depends(get_session)) -> UserResponse:
    """Get user by ID"""
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse.model_validate(user)

@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, payload: UserUpdate, session: Session = Depends(get_session)) -> UserResponse:
    """Update user by ID"""
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if email already exists (if being updated)
    if payload.email and payload.email != user.email:
        statement = select(User).where(User.email == payload.email, User.id != user_id)
        existing_user = session.exec(statement).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already exists")
    
    # Update user
    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user, key, value)
    
    session.add(user)
    session.commit()
    session.refresh(user)
    return UserResponse.model_validate(user)

@router.delete("/{user_id}", status_code=204)
def delete_user(user_id: int, session: Session = Depends(get_session)):
    """Delete user by ID"""
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    session.delete(user)
    session.commit()
    return None
