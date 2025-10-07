from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from typing import List
from ...models.user import User, UserCreate, UserUpdate, UserResponse, UserRegister, UserLogin, UserLoginResponse
from ...core.database import get_session
from ...core.security import hash_password, verify_password, create_access_token
from ...core.settings import get_settings

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/", response_model=List[UserResponse])
def list_users(session: Session = Depends(get_session)) -> List[UserResponse]:
    """Get all users"""
    statement = select(User).order_by(User.updated_at.desc())
    users = session.exec(statement).all()
    return [UserResponse.model_validate(user) for user in users]

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

@router.post("/register", response_model=UserLoginResponse, status_code=201)
def register_user(payload: UserRegister, session: Session = Depends(get_session)) -> UserLoginResponse:
    """Register a new user and return access token"""
    # Check if email already exists
    statement = select(User).where(User.email == payload.email)
    existing_user = session.exec(statement).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already exists")
    
    # Hash password and create user
    user_data = payload.model_dump()
    user_data['password'] = hash_password(user_data['password'])
    user_data['active'] = True  # Activate user automatically on registration
    
    # Create new user
    user = User(**user_data)
    session.add(user)
    session.commit()
    session.refresh(user)
    
    # Create access token immediately
    settings = get_settings()
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email},
        expires_minutes=settings.access_token_expire_minutes
    )
    
    return UserLoginResponse(
        access_token=access_token,
        user=UserResponse.model_validate(user)
    )

@router.post("/login", response_model=UserLoginResponse)
def login_user(payload: UserLogin, session: Session = Depends(get_session)) -> UserLoginResponse:
    """Login user and return access token"""
    # Find user by email
    statement = select(User).where(User.email == payload.email)
    user = session.exec(statement).first()
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Verify password
    if not verify_password(payload.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Check if user is active
    if not user.active:
        raise HTTPException(status_code=401, detail="User account is disabled")
    
    # Create access token
    settings = get_settings()
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email},
        expires_minutes=settings.access_token_expire_minutes
    )
    
    return UserLoginResponse(
        access_token=access_token,
        user=UserResponse.model_validate(user)
    )

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
