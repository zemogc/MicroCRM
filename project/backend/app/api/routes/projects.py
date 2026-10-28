from fastapi import APIRouter, HTTPException, Query
from sqlmodel import Session, select
from typing import Optional
from ...models.project import Project, ProjectCreate, ProjectUpdate, ProjectResponse
from ...models.user import User
from ...models.project_role import ProjectRole
from ...models.client import Client
from ...models.pagination import PaginatedResponse
from ...core.auth import CurrentUser, SessionDep
from ...core.cascade import delete_project_tree
from ...core.clock import utcnow
from ...core.permissions import accessible_project_ids, get_accessible_project, get_owned_project
from ...core.query import apply_ordering, count_rows

router = APIRouter(prefix="/projects", tags=["projects"])

DEFAULT_ROLES = [
    ("Administrador", "Administrador del proyecto"),
    ("Desarrollador", "Desarrollador del proyecto"),
    ("Revisor", "Revisor del proyecto"),
]


def build_project_response(project: Project, session: Session) -> ProjectResponse:
    """Project with its creator and client information"""
    creator = session.get(User, project.id_user)
    client = session.get(Client, project.client_id) if project.client_id else None
    project_data = project.model_dump()
    project_data['creator_name'] = creator.name if creator else "Unknown User"
    project_data['creator_email'] = creator.email if creator else "Unknown User"
    project_data['client_name'] = client.name if client else None
    return ProjectResponse.model_validate(project_data)


def validate_client(session: Session, client_id: Optional[int], owner: User) -> None:
    """A project can only be linked to a client of its owner's portfolio"""
    if client_id is None:
        return
    client = session.get(Client, client_id)
    if not client or client.owner_id != owner.id:
        raise HTTPException(status_code=400, detail="client_id does not belong to your clients")


@router.get("/", response_model=PaginatedResponse[ProjectResponse])
def list_projects(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=10, ge=1, le=100, description="Number of records to return"),
    order_by: str = Query(default="updated_at", description="Field to order by"),
    order_dir: str = Query(default="desc", description="Order direction (asc or desc)"),
    search: Optional[str] = Query(default=None, description="Search by name or description"),
    creator_id: Optional[int] = Query(default=None, description="Filter by creator ID"),
    client_id: Optional[int] = Query(default=None, description="Filter by client ID"),
) -> PaginatedResponse[ProjectResponse]:
    """Projects the current user owns or collaborates on, with filtering and ordering"""
    statement = select(Project).where(Project.id.in_(accessible_project_ids(current_user.id)))

    if search:
        search_filter = f"%{search}%"
        statement = statement.where(
            (Project.name.like(search_filter)) | (Project.description.like(search_filter))
        )

    if creator_id is not None:
        statement = statement.where(Project.id_user == creator_id)

    if client_id is not None:
        statement = statement.where(Project.client_id == client_id)

    total = count_rows(session, statement)
    statement = apply_ordering(statement, Project, order_by, order_dir, default="updated_at")
    projects = session.exec(statement.offset(skip).limit(limit)).all()

    return PaginatedResponse(
        items=[build_project_response(project, session) for project in projects],
        total=total,
        skip=skip,
        limit=limit,
        has_more=(skip + limit) < total
    )

@router.post("/", response_model=ProjectResponse, status_code=201)
def create_project(
    payload: ProjectCreate,
    session: SessionDep,
    current_user: CurrentUser
) -> ProjectResponse:
    """Create a new project owned by the current user, with its default roles"""
    validate_client(session, payload.client_id, current_user)
    project = Project(**payload.model_dump(), id_user=current_user.id)
    session.add(project)
    session.flush()  # Get the project id for the roles

    for name, description in DEFAULT_ROLES:
        session.add(ProjectRole(name=name, description=description, project_id=project.id))

    session.commit()
    session.refresh(project)
    return build_project_response(project, session)

@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: int, session: SessionDep, current_user: CurrentUser) -> ProjectResponse:
    """Get project by ID (owner or collaborator)"""
    project = get_accessible_project(session, project_id, current_user)
    return build_project_response(project, session)

@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: int,
    payload: ProjectUpdate,
    session: SessionDep,
    current_user: CurrentUser
) -> ProjectResponse:
    """Update project by ID (owner only)"""
    project = get_owned_project(session, project_id, current_user)

    update_data = payload.model_dump(exclude_unset=True)
    if update_data.get("client_id") is not None:
        validate_client(session, update_data["client_id"], current_user)
    if update_data.get("name") is None:
        update_data.pop("name", None)  # name is required, null means "unchanged"
    for key, value in update_data.items():
        setattr(project, key, value)
    project.updated_at = utcnow()

    session.add(project)
    session.commit()
    session.refresh(project)
    return build_project_response(project, session)

@router.delete("/{project_id}", status_code=204)
def delete_project(project_id: int, session: SessionDep, current_user: CurrentUser):
    """Delete project with its tasks, members and roles (owner only)"""
    get_owned_project(session, project_id, current_user)
    delete_project_tree(session, project_id)
    session.commit()
    return None
