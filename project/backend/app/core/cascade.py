"""
Explicit deletes in dependency order.

project_members -> project_roles is ON DELETE RESTRICT, so relying on the
database cascade from projects can fail depending on the order the engine
processes the cascades. Deleting the children first is deterministic on
MySQL and SQLite.
"""

from sqlmodel import Session, select, delete, update
from ..models.project import Project
from ..models.project_member import ProjectMember
from ..models.project_role import ProjectRole
from ..models.task import Task
from ..models.user import User


def delete_project_tree(session: Session, project_id: int) -> None:
    """Delete a project with its members, roles and tasks (does not commit)"""
    session.exec(delete(ProjectMember).where(ProjectMember.project_id == project_id))
    session.exec(delete(Task).where(Task.project_id == project_id))
    session.exec(delete(ProjectRole).where(ProjectRole.project_id == project_id))
    session.exec(delete(Project).where(Project.id == project_id))


def delete_user_tree(session: Session, user: User) -> None:
    """Delete a user, the projects they own and their memberships (does not commit)"""
    owned_ids = session.exec(select(Project.id).where(Project.id_user == user.id)).all()
    for project_id in owned_ids:
        delete_project_tree(session, project_id)

    session.exec(delete(ProjectMember).where(ProjectMember.user_id == user.id))
    session.exec(update(Task).where(Task.assigned_to == user.id).values(assigned_to=None))
    session.delete(user)
