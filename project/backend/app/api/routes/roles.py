from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from typing import List
from ...models.role import Role, RoleCreate, RoleUpdate, RoleResponse
from ...core.database import get_session

router = APIRouter(prefix="/roles", tags=["roles"])

@router.get("/", response_model=List[RoleResponse])
def list_roles(session: Session = Depends(get_session)) -> List[RoleResponse]:
    """Get all roles"""
    statement = select(Role).order_by(Role.name)
    roles = session.exec(statement).all()
    return [RoleResponse.model_validate(role) for role in roles]

@router.post("/", response_model=RoleResponse, status_code=201)
def create_role(payload: RoleCreate, session: Session = Depends(get_session)) -> RoleResponse:
    """Create a new role"""
    # Check if role name already exists
    statement = select(Role).where(Role.name.ilike(payload.name))
    existing_role = session.exec(statement).first()
    if existing_role:
        raise HTTPException(status_code=400, detail="Role name already exists")
    
    # Create new role
    role = Role(**payload.model_dump())
    session.add(role)
    session.commit()
    session.refresh(role)
    return RoleResponse.model_validate(role)

@router.get("/{role_id}", response_model=RoleResponse)
def get_role(role_id: int, session: Session = Depends(get_session)) -> RoleResponse:
    """Get role by ID"""
    role = session.get(Role, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return RoleResponse.model_validate(role)

@router.put("/{role_id}", response_model=RoleResponse)
def update_role(role_id: int, payload: RoleUpdate, session: Session = Depends(get_session)) -> RoleResponse:
    """Update role by ID"""
    role = session.get(Role, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    # Check if new name already exists (if being updated)
    if payload.name and payload.name.lower() != role.name.lower():
        statement = select(Role).where(Role.name.ilike(payload.name), Role.id != role_id)
        existing_role = session.exec(statement).first()
        if existing_role:
            raise HTTPException(status_code=400, detail="Role name already exists")
    
    # Update role
    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(role, key, value)
    
    session.add(role)
    session.commit()
    session.refresh(role)
    return RoleResponse.model_validate(role)

@router.delete("/{role_id}", status_code=204)
def delete_role(role_id: int, session: Session = Depends(get_session)):
    """Delete role by ID"""
    role = session.get(Role, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    session.delete(role)
    session.commit()
    return None


