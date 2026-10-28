"""
Project Permissions
===================
Access rules shared by the routes:

- The project creator (``Project.id_user``) is the owner and has full control.
- Users added through ``project_members`` are collaborators: they can see the
  project and change the status of the tasks assigned to them.
- Anyone else gets 404 for projects they cannot see, so ids are not leaked.
"""

from fastapi import HTTPException, status
from sqlmodel import Session, select, or_
from ..models.project import Project
from ..models.project_member import ProjectMember
from ..models.user import User


def accessible_project_ids(user_id: int):
    """Subquery with the ids of the projects a user owns or collaborates on"""
    member_of = select(ProjectMember.project_id).where(ProjectMember.user_id == user_id)
    return select(Project.id).where(or_(Project.id_user == user_id, Project.id.in_(member_of)))


def is_project_member(session: Session, project: Project, user_id: int) -> bool:
    """True if the user is the owner or a collaborator of the project"""
    if project.id_user == user_id:
        return True
    membership = session.exec(
        select(ProjectMember).where(
            ProjectMember.project_id == project.id,
            ProjectMember.user_id == user_id
        )
    ).first()
    return membership is not None


def get_accessible_project(session: Session, project_id: int, user: User) -> Project:
    """Return the project if the user can see it, otherwise 404"""
    project = session.get(Project, project_id)
    if not project or not is_project_member(session, project, user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project


def get_owned_project(session: Session, project_id: int, user: User) -> Project:
    """Return the project if the user owns it (404 if not visible, 403 if only a collaborator)"""
    project = get_accessible_project(session, project_id, user)
    if project.id_user != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the project owner can perform this action"
        )
    return project


def ensure_self(user: User, user_id: int) -> None:
    """Allow an action only over the authenticated user's own resources"""
    if user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own resources"
        )
