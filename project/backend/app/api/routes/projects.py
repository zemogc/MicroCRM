from fastapi import APIRouter, HTTPException, Depends, Request, Query
from sqlmodel import Session, select, func, col
from typing import List, Optional
from ...models.project import Project, ProjectCreate, ProjectUpdate, ProjectResponse
from ...models.user import User
from ...models.project_role import ProjectRole
from ...models.pagination import PaginatedResponse
from ...core.database import get_session
from ...core.auth import get_current_active_user
from ...core.rate_limit import rate_limit_api
from ...core.settings import get_settings

router = APIRouter(prefix="/projects", tags=["projects"])

@router.get("/", response_model=PaginatedResponse[ProjectResponse])
async def list_projects(
    request: Request,
    session: Session = Depends(get_session),
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=10, ge=1, le=100, description="Number of records to return"),
    order_by: str = Query(default="updated_at", description="Field to order by"),
    order_dir: str = Query(default="desc", description="Order direction (asc or desc)"),
    search: Optional[str] = Query(default=None, description="Search by name or description"),
    creator_id: Optional[int] = Query(default=None, description="Filter by creator ID"),
    current_user: User = Depends(get_current_active_user)
) -> PaginatedResponse[ProjectResponse]:
    """Get paginated list of projects with filtering and ordering"""
    settings = get_settings()
    await rate_limit_api(request, settings.rate_limit_api_per_min, str(current_user.id))
    
    # Base query
    statement = select(Project)
    
    # Apply filters
    if search:
        search_filter = f"%{search}%"
        statement = statement.where(
            (Project.name.like(search_filter)) | (Project.description.like(search_filter))
        )
    
    if creator_id is not None:
        statement = statement.where(Project.id_user == creator_id)
    
    # Get total count
    count_statement = select(func.count()).select_from(statement.subquery())
    total = session.exec(count_statement).one()
    
    # Apply ordering
    order_column = getattr(Project, order_by, Project.updated_at)
    if order_dir.lower() == "asc":
        statement = statement.order_by(col(order_column).asc())
    else:
        statement = statement.order_by(col(order_column).desc())
    
    # Apply pagination
    statement = statement.offset(skip).limit(limit)
    
    # Execute query
    projects = session.exec(statement).all()
    
    # Create response with creator information
    result = []
    for project in projects:
        creator = session.get(User, project.id_user)
        project_data = project.model_dump()
        project_data['creator_name'] = creator.name if creator else "Unknown User"
        project_data['creator_email'] = creator.email if creator else "Unknown User"
        result.append(ProjectResponse.model_validate(project_data))
    
    return PaginatedResponse(
        items=result,
        total=total,
        skip=skip,
        limit=limit,
        has_more=(skip + limit) < total
    )

@router.post("/", response_model=ProjectResponse, status_code=201)
async def create_project(
    request: Request,
    payload: ProjectCreate, 
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
) -> ProjectResponse:
    """Create a new project"""
    settings = get_settings()
    await rate_limit_api(request, settings.rate_limit_api_per_min, str(current_user.id))
    
    # Validate that the creator user exists
    user = session.get(User, payload.id_user)
    if not user:
        raise HTTPException(status_code=400, detail="id_user does not exist")
    
    # Create new project
    project = Project(**payload.model_dump())
    session.add(project)
    session.commit()
    session.refresh(project)
    
    # Create default roles for the project
    default_roles = [
        {"name": "Administrador", "description": "Administrador del proyecto", "project_id": project.id},
        {"name": "Desarrollador", "description": "Desarrollador del proyecto", "project_id": project.id},
        {"name": "Revisor", "description": "Revisor del proyecto", "project_id": project.id}
    ]
    
    for role_data in default_roles:
        role = ProjectRole(**role_data)
        session.add(role)
    
    session.commit()
    
    # Include creator information in response
    project_data = {
        'id': project.id,
        'name': project.name,
        'description': project.description,
        'id_user': project.id_user,
        'created_at': project.created_at,
        'updated_at': project.updated_at,
        'creator_name': user.name,
        'creator_email': user.email
    }
    
    return ProjectResponse.model_validate(project_data)

@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int, 
    request: Request,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
) -> ProjectResponse:
    """Get project by ID"""
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Include creator information
    creator = session.get(User, project.id_user)
    project_data = {
        'id': project.id,
        'name': project.name,
        'description': project.description,
        'id_user': project.id_user,
        'created_at': project.created_at,
        'updated_at': project.updated_at,
        'creator_name': creator.name if creator else "Unknown User",
        'creator_email': creator.email if creator else "Unknown User"
    }
    
    return ProjectResponse.model_validate(project_data)

@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int, 
    payload: ProjectUpdate, 
    request: Request,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
) -> ProjectResponse:
    """Update project by ID"""
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Update project
    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(project, key, value)
    
    session.add(project)
    session.commit()
    session.refresh(project)
    
    # Include creator information in response
    creator = session.get(User, project.id_user)
    project_data = {
        'id': project.id,
        'name': project.name,
        'description': project.description,
        'id_user': project.id_user,
        'created_at': project.created_at,
        'updated_at': project.updated_at,
        'creator_name': creator.name if creator else "Unknown User",
        'creator_email': creator.email if creator else "Unknown User"
    }
    
    return ProjectResponse.model_validate(project_data)

@router.delete("/{project_id}", status_code=204)
async def delete_project(
    project_id: int, 
    request: Request,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """Delete project by ID"""
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    session.delete(project)
    session.commit()
    return None
