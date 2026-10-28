from fastapi import APIRouter, HTTPException, Query
from sqlmodel import Session, select
from typing import List, Optional
from ...models.project_member import ProjectMember, ProjectMemberCreate, ProjectMemberUpdate, ProjectMemberResponse
from ...models.user import User
from ...models.project_role import ProjectRole
from ...models.project import Project
from ...models.pagination import PaginatedResponse
from ...core.auth import CurrentUser, SessionDep
from ...core.permissions import accessible_project_ids, ensure_self, get_accessible_project, get_owned_project
from ...core.query import apply_ordering, count_rows

router = APIRouter(prefix="/project-members", tags=["project-members"])

def enrich_project_member_response(member: ProjectMember, session: Session) -> ProjectMemberResponse:
    """Helper function to enrich project member with related information"""
    project = session.get(Project, member.project_id)
    user = session.get(User, member.user_id)
    project_role = session.get(ProjectRole, member.project_role_id)

    member_data = member.model_dump()
    member_data['project_name'] = project.name if project else "Unknown Project"
    member_data['user_name'] = user.name if user else "Unknown User"
    member_data['user_email'] = user.email if user else "Unknown Email"
    member_data['role_name'] = project_role.name if project_role else "Unknown Role"
    member_data['role_description'] = project_role.description if project_role else None

    return ProjectMemberResponse.model_validate(member_data)

def validate_project_role(session: Session, role_id: int, project_id: int) -> ProjectRole:
    """The role must exist and belong to the same project"""
    project_role = session.get(ProjectRole, role_id)
    if not project_role or project_role.project_id != project_id:
        raise HTTPException(status_code=400, detail="project_role_id does not belong to this project")
    return project_role

def get_member_as_owner(session: Session, member_id: int, current_user: User) -> ProjectMember:
    """Membership that only the project owner can modify"""
    member = session.get(ProjectMember, member_id)
    if not member:
        raise HTTPException(status_code=404, detail="Project member not found")
    get_owned_project(session, member.project_id, current_user)
    return member

@router.get("/", response_model=PaginatedResponse[ProjectMemberResponse])
def list_project_members(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=10, ge=1, le=100, description="Number of records to return"),
    order_by: str = Query(default="created_at", description="Field to order by"),
    order_dir: str = Query(default="desc", description="Order direction (asc or desc)"),
    project_id: Optional[int] = Query(default=None, description="Filter by project ID"),
    user_id: Optional[int] = Query(default=None, description="Filter by user ID"),
) -> PaginatedResponse[ProjectMemberResponse]:
    """Memberships of the projects the current user can see"""
    statement = select(ProjectMember).where(
        ProjectMember.project_id.in_(accessible_project_ids(current_user.id))
    )

    if project_id is not None:
        statement = statement.where(ProjectMember.project_id == project_id)

    if user_id is not None:
        statement = statement.where(ProjectMember.user_id == user_id)

    total = count_rows(session, statement)
    statement = apply_ordering(statement, ProjectMember, order_by, order_dir, default="created_at")
    members = session.exec(statement.offset(skip).limit(limit)).all()

    return PaginatedResponse(
        items=[enrich_project_member_response(member, session) for member in members],
        total=total,
        skip=skip,
        limit=limit,
        has_more=(skip + limit) < total
    )

@router.get("/project/{project_id}", response_model=List[ProjectMemberResponse])
def list_project_members_by_project(project_id: int, session: SessionDep, current_user: CurrentUser) -> List[ProjectMemberResponse]:
    """Get all members for a specific project"""
    get_accessible_project(session, project_id, current_user)

    statement = select(ProjectMember).where(ProjectMember.project_id == project_id).order_by(ProjectMember.created_at.desc())
    members = session.exec(statement).all()
    return [enrich_project_member_response(member, session) for member in members]

@router.get("/user/{user_id}", response_model=List[ProjectMemberResponse])
def list_project_members_by_user(user_id: int, session: SessionDep, current_user: CurrentUser) -> List[ProjectMemberResponse]:
    """Get all projects where the current user is a member"""
    ensure_self(current_user, user_id)

    statement = select(ProjectMember).where(ProjectMember.user_id == user_id).order_by(ProjectMember.created_at.desc())
    members = session.exec(statement).all()
    return [enrich_project_member_response(member, session) for member in members]

@router.post("/", response_model=ProjectMemberResponse, status_code=201)
def create_project_member(
    payload: ProjectMemberCreate,
    session: SessionDep,
    current_user: CurrentUser
) -> ProjectMemberResponse:
    """Add a user as a member to a project (owner only)"""
    project = get_owned_project(session, payload.project_id, current_user)

    if not session.get(User, payload.user_id):
        raise HTTPException(status_code=400, detail="user_id does not exist")

    if payload.user_id == project.id_user:
        raise HTTPException(status_code=400, detail="The project owner is already part of the project")

    validate_project_role(session, payload.project_role_id, project.id)

    existing_member = session.exec(
        select(ProjectMember).where(
            ProjectMember.project_id == payload.project_id,
            ProjectMember.user_id == payload.user_id
        )
    ).first()

    if existing_member:
        raise HTTPException(status_code=400, detail="User is already a member of this project")

    member = ProjectMember(**payload.model_dump())
    session.add(member)
    session.commit()
    session.refresh(member)
    return enrich_project_member_response(member, session)

@router.get("/{member_id}", response_model=ProjectMemberResponse)
def get_project_member(member_id: int, session: SessionDep, current_user: CurrentUser) -> ProjectMemberResponse:
    """Get project member by ID"""
    member = session.get(ProjectMember, member_id)
    if not member:
        raise HTTPException(status_code=404, detail="Project member not found")
    get_accessible_project(session, member.project_id, current_user)
    return enrich_project_member_response(member, session)

@router.put("/{member_id}", response_model=ProjectMemberResponse)
def update_project_member(
    member_id: int,
    payload: ProjectMemberUpdate,
    session: SessionDep,
    current_user: CurrentUser
) -> ProjectMemberResponse:
    """Update project member role by ID (owner only)"""
    member = get_member_as_owner(session, member_id, current_user)
    validate_project_role(session, payload.project_role_id, member.project_id)

    member.project_role_id = payload.project_role_id
    session.add(member)
    session.commit()
    session.refresh(member)
    return enrich_project_member_response(member, session)

@router.delete("/{member_id}", status_code=204)
def delete_project_member(member_id: int, session: SessionDep, current_user: CurrentUser):
    """Remove user from project (owner only)"""
    member = get_member_as_owner(session, member_id, current_user)
    session.delete(member)
    session.commit()
    return None
