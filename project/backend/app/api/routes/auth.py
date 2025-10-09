from fastapi import APIRouter, HTTPException, Depends, Request
from sqlmodel import Session, select
from ...models.user import User, UserRegister, UserLogin, UserLoginResponse, UserResponse
from ...core.database import get_session
from ...core.security import hash_password, verify_password, create_access_token
from ...core.settings import get_settings
from ...core.auth import get_current_active_user
from ...core.rate_limit import rate_limit_auth, rate_limit_api

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/register", response_model=UserLoginResponse, status_code=201)
async def register_user(
    request: Request,
    payload: UserRegister, 
    session: Session = Depends(get_session)
) -> UserLoginResponse:
    """Register a new user and return access token"""
    # Apply rate limiting (5 req/min by IP)
    settings = get_settings()
    await rate_limit_auth(request, settings.rate_limit_auth_per_min)
    
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
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email},
        expires_minutes=settings.access_token_expire_minutes
    )
    
    return UserLoginResponse(
        access_token=access_token,
        user=UserResponse.model_validate(user)
    )

@router.post("/login", response_model=UserLoginResponse)
async def login_user(
    request: Request,
    payload: UserLogin, 
    session: Session = Depends(get_session)
) -> UserLoginResponse:
    """Login user and return access token"""
    # Apply rate limiting (5 req/min by IP)
    settings = get_settings()
    await rate_limit_auth(request, settings.rate_limit_auth_per_min)
    
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
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email},
        expires_minutes=settings.access_token_expire_minutes
    )
    
    return UserLoginResponse(
        access_token=access_token,
        user=UserResponse.model_validate(user)
    )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session)
) -> UserResponse:
    """Get current authenticated user information"""
    settings = get_settings()
    await rate_limit_api(request, settings.rate_limit_api_per_min, str(current_user.id))
    return UserResponse.model_validate(current_user)
