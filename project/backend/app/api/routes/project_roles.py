from fastapi import APIRouter, HTTPException, Depends, Request, Query
from sqlmodel import Session, select, func, col
from typing import List, Optional
from ...models.project_role import ProjectRole, ProjectRoleCreate, ProjectRoleUpdate, ProjectRoleResponse
from ...models.project import Project
from ...models.user import User
from ...models.pagination import PaginatedResponse
from ...core.database import get_session
from ...core.auth import get_current_active_user
from ...core.rate_limit import rate_limit_api
from ...core.settings import get_settings

router = APIRouter(prefix="/project-roles", tags=["project-roles"])

@router.get("/project/{project_id}", response_model=List[ProjectRoleResponse])
def list_project_roles_by_project(project_id: int, session: Session = Depends(get_session)) -> List[ProjectRoleResponse]:
    """Get all roles for a specific project"""
    # Validate project exists
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    statement = select(ProjectRole).where(ProjectRole.project_id == project_id).order_by(ProjectRole.name.asc())
    roles = session.exec(statement).all()
    
    # Enrich with project name
    enriched_roles = []
    for role in roles:
        role_data = role.model_dump()
        role_data['project_name'] = project.name
        enriched_roles.append(ProjectRoleResponse.model_validate(role_data))
    
    return enriched_roles

@router.post("/", response_model=ProjectRoleResponse, status_code=201)
async def create_project_role(
    request: Request,
    payload: ProjectRoleCreate, 
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
) -> ProjectRoleResponse:
    """Create a new role for a project"""
    settings = get_settings()
    await rate_limit_api(request, settings.rate_limit_api_per_min, str(current_user.id))
    
    # Validate that the project exists
    project = session.get(Project, payload.project_id)
    if not project:
        raise HTTPException(status_code=400, detail="project_id does not exist")
    
    # Check if role name already exists for this project
    existing_role = session.exec(
        select(ProjectRole).where(
            ProjectRole.project_id == payload.project_id,
            ProjectRole.name == payload.name
        )
    ).first()
    
    if existing_role:
        raise HTTPException(status_code=400, detail="Role name already exists for this project")
    
    # Create new project role
    role = ProjectRole(**payload.model_dump())
    session.add(role)
    session.commit()
    session.refresh(role)
    
    # Enrich with project name
    role_data = role.model_dump()
    role_data['project_name'] = project.name
    
    return ProjectRoleResponse.model_validate(role_data)

@router.get("/{role_id}", response_model=ProjectRoleResponse)
def get_project_role(role_id: int, session: Session = Depends(get_session)) -> ProjectRoleResponse:
    """Get project role by ID"""
    role = session.get(ProjectRole, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Project role not found")
    
    # Get project information
    project = session.get(Project, role.project_id)
    
    # Enrich with project name
    role_data = role.model_dump()
    role_data['project_name'] = project.name if project else "Unknown Project"
    
    return ProjectRoleResponse.model_validate(role_data)

@router.put("/{role_id}", response_model=ProjectRoleResponse)
def update_project_role(role_id: int, payload: ProjectRoleUpdate, session: Session = Depends(get_session)) -> ProjectRoleResponse:
    """Update project role by ID"""
    role = session.get(ProjectRole, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Project role not found")
    
    # Update role
    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(role, key, value)
    
    session.add(role)
    session.commit()
    session.refresh(role)
    
    # Get project information
    project = session.get(Project, role.project_id)
    
    # Enrich with project name
    role_data = role.model_dump()
    role_data['project_name'] = project.name if project else "Unknown Project"
    
    return ProjectRoleResponse.model_validate(role_data)

@router.delete("/{role_id}", status_code=204)
def delete_project_role(role_id: int, session: Session = Depends(get_session)):
    """Delete project role by ID"""
    role = session.get(ProjectRole, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Project role not found")
    
    session.delete(role)
    session.commit()
    return None
