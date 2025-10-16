from fastapi import APIRouter, HTTPException, Depends, Request, Query
from sqlmodel import Session, select, func, col
from typing import List, Optional
from ...models.project_member import ProjectMember, ProjectMemberCreate, ProjectMemberUpdate, ProjectMemberResponse
from ...models.user import User
from ...models.project_role import ProjectRole
from ...models.project import Project
from ...models.pagination import PaginatedResponse
from ...core.database import get_session
from ...core.auth import get_current_active_user
from ...core.rate_limit import rate_limit_api
from ...core.settings import get_settings

router = APIRouter(prefix="/project-members", tags=["project-members"])

def enrich_project_member_response(member: ProjectMember, session: Session) -> ProjectMemberResponse:
    """Helper function to enrich project member with related information"""
    # Get project information
    project = session.get(Project, member.project_id)
    
    # Get user information
    user = session.get(User, member.user_id)
    
    # Get project role information
    project_role = session.get(ProjectRole, member.project_role_id)
    
    # Create enriched member data
    member_data = member.model_dump()
    member_data['project_name'] = project.name if project else "Unknown Project"
    member_data['user_name'] = user.name if user else "Unknown User"
    member_data['user_email'] = user.email if user else "Unknown Email"
    member_data['role_name'] = project_role.name if project_role else "Unknown Role"
    member_data['role_description'] = project_role.description if project_role else None
    
    return ProjectMemberResponse.model_validate(member_data)

@router.get("/", response_model=PaginatedResponse[ProjectMemberResponse])
async def list_project_members(
    request: Request,
    session: Session = Depends(get_session),
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=10, ge=1, le=100, description="Number of records to return"),
    order_by: str = Query(default="created_at", description="Field to order by"),
    order_dir: str = Query(default="desc", description="Order direction (asc or desc)"),
    project_id: Optional[int] = Query(default=None, description="Filter by project ID"),
    user_id: Optional[int] = Query(default=None, description="Filter by user ID"),
    current_user: User = Depends(get_current_active_user)
) -> PaginatedResponse[ProjectMemberResponse]:
    """Get paginated list of project members with filtering and ordering"""
    settings = get_settings()
    await rate_limit_api(request, settings.rate_limit_api_per_min, str(current_user.id))
    
    # Base query
    statement = select(ProjectMember)
    
    # Apply filters
    if project_id is not None:
        statement = statement.where(ProjectMember.project_id == project_id)
    
    if user_id is not None:
        statement = statement.where(ProjectMember.user_id == user_id)
    
    # Get total count
    count_statement = select(func.count()).select_from(statement.subquery())
    total = session.exec(count_statement).one()
    
    # Apply ordering
    order_column = getattr(ProjectMember, order_by, ProjectMember.created_at)
    if order_dir.lower() == "asc":
        statement = statement.order_by(col(order_column).asc())
    else:
        statement = statement.order_by(col(order_column).desc())
    
    # Apply pagination
    statement = statement.offset(skip).limit(limit)
    
    # Execute query
    members = session.exec(statement).all()
    
    return PaginatedResponse(
        items=[enrich_project_member_response(member, session) for member in members],
        total=total,
        skip=skip,
        limit=limit,
        has_more=(skip + limit) < total
    )

@router.get("/project/{project_id}", response_model=List[ProjectMemberResponse])
def list_project_members_by_project(project_id: int, session: Session = Depends(get_session)) -> List[ProjectMemberResponse]:
    """Get all members for a specific project"""
    # Validate project exists
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    statement = select(ProjectMember).where(ProjectMember.project_id == project_id).order_by(ProjectMember.created_at.desc())
    members = session.exec(statement).all()
    return [enrich_project_member_response(member, session) for member in members]

@router.get("/user/{user_id}", response_model=List[ProjectMemberResponse])
def list_project_members_by_user(user_id: int, session: Session = Depends(get_session)) -> List[ProjectMemberResponse]:
    """Get all projects where a user is a member"""
    # Validate user exists
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    statement = select(ProjectMember).where(ProjectMember.user_id == user_id).order_by(ProjectMember.created_at.desc())
    members = session.exec(statement).all()
    return [enrich_project_member_response(member, session) for member in members]

@router.post("/", response_model=ProjectMemberResponse, status_code=201)
async def create_project_member(
    request: Request,
    payload: ProjectMemberCreate, 
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
) -> ProjectMemberResponse:
    """Add a user as a member to a project"""
    settings = get_settings()
    await rate_limit_api(request, settings.rate_limit_api_per_min, str(current_user.id))
    
    # Validate that the project exists
    project = session.get(Project, payload.project_id)
    if not project:
        raise HTTPException(status_code=400, detail="project_id does not exist")
    
    # Validate that the user exists
    user = session.get(User, payload.user_id)
    if not user:
        raise HTTPException(status_code=400, detail="user_id does not exist")
    
    # Validate that the project role exists
    project_role = session.get(ProjectRole, payload.project_role_id)
    if not project_role:
        raise HTTPException(status_code=400, detail="project_role_id does not exist")
    
    # Check if user is already a member of this project
    existing_member = session.exec(
        select(ProjectMember).where(
            ProjectMember.project_id == payload.project_id,
            ProjectMember.user_id == payload.user_id
        )
    ).first()
    
    if existing_member:
        raise HTTPException(status_code=400, detail="User is already a member of this project")
    
    # Create new project member
    member = ProjectMember(**payload.model_dump())
    session.add(member)
    session.commit()
    session.refresh(member)
    return enrich_project_member_response(member, session)

@router.get("/{member_id}", response_model=ProjectMemberResponse)
def get_project_member(member_id: int, session: Session = Depends(get_session)) -> ProjectMemberResponse:
    """Get project member by ID"""
    member = session.get(ProjectMember, member_id)
    if not member:
        raise HTTPException(status_code=404, detail="Project member not found")
    return enrich_project_member_response(member, session)

@router.put("/{member_id}", response_model=ProjectMemberResponse)
def update_project_member(member_id: int, payload: ProjectMemberUpdate, session: Session = Depends(get_session)) -> ProjectMemberResponse:
    """Update project member role by ID"""
    member = session.get(ProjectMember, member_id)
    if not member:
        raise HTTPException(status_code=404, detail="Project member not found")
    
    # Validate that the project role exists
    project_role = session.get(ProjectRole, payload.project_role_id)
    if not project_role:
        raise HTTPException(status_code=400, detail="project_role_id does not exist")
    
    # Update member
    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(member, key, value)
    
    session.add(member)
    session.commit()
    session.refresh(member)
    return enrich_project_member_response(member, session)

@router.delete("/{member_id}", status_code=204)
def delete_project_member(member_id: int, session: Session = Depends(get_session)):
    """Remove user from project"""
    member = session.get(ProjectMember, member_id)
    if not member:
        raise HTTPException(status_code=404, detail="Project member not found")
    
    session.delete(member)
    session.commit()
    return None
