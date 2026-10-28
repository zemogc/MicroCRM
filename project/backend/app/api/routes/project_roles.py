from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select
from typing import List
from ...models.project_role import ProjectRole, ProjectRoleCreate, ProjectRoleUpdate, ProjectRoleResponse
from ...models.project_member import ProjectMember
from ...models.project import Project
from ...models.user import User
from ...core.auth import CurrentUser, SessionDep
from ...core.permissions import get_accessible_project, get_owned_project

router = APIRouter(prefix="/project-roles", tags=["project-roles"])

def build_role_response(role: ProjectRole, project: Project) -> ProjectRoleResponse:
    role_data = role.model_dump()
    role_data['project_name'] = project.name
    return ProjectRoleResponse.model_validate(role_data)

def ensure_unique_name(session: Session, project_id: int, name: str, exclude_id: int | None = None) -> None:
    statement = select(ProjectRole).where(ProjectRole.project_id == project_id, ProjectRole.name == name)
    if exclude_id is not None:
        statement = statement.where(ProjectRole.id != exclude_id)
    if session.exec(statement).first():
        raise HTTPException(status_code=400, detail="Role name already exists for this project")

def get_role_as_owner(session: Session, role_id: int, current_user: User) -> tuple[ProjectRole, Project]:
    role = session.get(ProjectRole, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Project role not found")
    project = get_owned_project(session, role.project_id, current_user)
    return role, project

@router.get("/project/{project_id}", response_model=List[ProjectRoleResponse])
def list_project_roles_by_project(project_id: int, session: SessionDep, current_user: CurrentUser) -> List[ProjectRoleResponse]:
    """Get all roles for a specific project"""
    project = get_accessible_project(session, project_id, current_user)

    statement = select(ProjectRole).where(ProjectRole.project_id == project_id).order_by(ProjectRole.name.asc())
    return [build_role_response(role, project) for role in session.exec(statement).all()]

@router.post("/", response_model=ProjectRoleResponse, status_code=201)
def create_project_role(payload: ProjectRoleCreate, session: SessionDep, current_user: CurrentUser) -> ProjectRoleResponse:
    """Create a new role for a project (owner only)"""
    project = get_owned_project(session, payload.project_id, current_user)
    ensure_unique_name(session, project.id, payload.name)

    role = ProjectRole(**payload.model_dump())
    session.add(role)
    session.commit()
    session.refresh(role)
    return build_role_response(role, project)

@router.get("/{role_id}", response_model=ProjectRoleResponse)
def get_project_role(role_id: int, session: SessionDep, current_user: CurrentUser) -> ProjectRoleResponse:
    """Get project role by ID"""
    role = session.get(ProjectRole, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Project role not found")
    project = get_accessible_project(session, role.project_id, current_user)
    return build_role_response(role, project)

@router.put("/{role_id}", response_model=ProjectRoleResponse)
def update_project_role(role_id: int, payload: ProjectRoleUpdate, session: SessionDep, current_user: CurrentUser) -> ProjectRoleResponse:
    """Update project role by ID (owner only)"""
    role, project = get_role_as_owner(session, role_id, current_user)

    update_data = payload.model_dump(exclude_unset=True)
    if update_data.get("name"):
        ensure_unique_name(session, project.id, update_data["name"], exclude_id=role.id)

    for key, value in update_data.items():
        setattr(role, key, value)

    session.add(role)
    session.commit()
    session.refresh(role)
    return build_role_response(role, project)

@router.delete("/{role_id}", status_code=204)
def delete_project_role(role_id: int, session: SessionDep, current_user: CurrentUser):
    """Delete project role by ID (owner only, the role must not be in use)"""
    role, _ = get_role_as_owner(session, role_id, current_user)

    in_use = session.exec(select(ProjectMember).where(ProjectMember.project_role_id == role.id)).first()
    if in_use:
        raise HTTPException(status_code=400, detail="The role is assigned to project members")

    session.delete(role)
    session.commit()
    return None
