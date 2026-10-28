from fastapi import APIRouter, HTTPException, Depends, Request
from sqlmodel import Session, select
from ...models.user import User, UserRegister, UserLogin, UserLoginResponse, UserResponse, PasswordChange
from ...core.database import get_session
from ...core.security import hash_password, verify_password, create_access_token
from ...core.settings import get_settings
from ...core.auth import CurrentUser, SessionDep
from ...core.clock import utcnow
from ...core.rate_limit import rate_limit_auth

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
def get_current_user_info(current_user: CurrentUser) -> UserResponse:
    """Get current authenticated user information"""
    return UserResponse.model_validate(current_user)

@router.post("/change-password", status_code=204)
async def change_password(
    request: Request,
    payload: PasswordChange,
    session: SessionDep,
    current_user: CurrentUser
):
    """Change the password of the current user (requires the current one)"""
    # Same limit as login: this endpoint also verifies a password
    await rate_limit_auth(request, get_settings().rate_limit_auth_per_min)

    if not verify_password(payload.current_password, current_user.password):
        raise HTTPException(status_code=400, detail="La contraseña actual no es correcta")
    if payload.current_password == payload.new_password:
        raise HTTPException(status_code=400, detail="La nueva contraseña debe ser diferente a la actual")

    current_user.password = hash_password(payload.new_password)
    current_user.updated_at = utcnow()
    session.add(current_user)
    session.commit()
    return None
