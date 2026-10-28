from datetime import timedelta
from fastapi import APIRouter
from sqlmodel import select, func
from ...models.client import Client, CLIENT_STATUSES
from ...models.project import Project
from ...models.project_member import ProjectMember
from ...models.task import Task, TASK_STATUSES
from ...core.auth import CurrentUser, SessionDep
from ...core.clock import utcnow
from ...core.permissions import accessible_project_ids
from ...core.task_automation import update_overdue_tasks
from .projects import build_project_response
from .tasks import enrich_task_response

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

DUE_SOON_DAYS = 7
OPEN_STATUSES = ["pending", "in_progress", "overdue", "in_review"]


def count_by(session, column, statement, keys: list[str]) -> dict[str, int]:
    rows = session.exec(statement.group_by(column)).all()
    counts = {key: 0 for key in keys}
    counts.update({key: total for key, total in rows})
    return counts


@router.get("/summary")
def get_summary(session: SessionDep, current_user: CurrentUser) -> dict:
    """Key figures for the home screen of the current user"""
    update_overdue_tasks(session)

    owned = session.exec(
        select(func.count()).select_from(Project).where(Project.id_user == current_user.id)
    ).one()
    collaborating = session.exec(
        select(func.count()).select_from(ProjectMember).where(ProjectMember.user_id == current_user.id)
    ).one()

    tasks_by_status = count_by(
        session, Task.status,
        select(Task.status, func.count()).where(Task.assigned_to == current_user.id),
        TASK_STATUSES,
    )
    assigned_total = sum(tasks_by_status.values())
    completion_rate = round(tasks_by_status["completed"] * 100 / assigned_total) if assigned_total else 0

    clients_by_status = count_by(
        session, Client.status,
        select(Client.status, func.count()).where(Client.owner_id == current_user.id),
        CLIENT_STATUSES,
    )

    # Open tasks assigned to me that are late or due in the next days
    due_soon = session.exec(
        select(Task)
        .where(
            Task.assigned_to == current_user.id,
            Task.status.in_(OPEN_STATUSES),
            Task.due_date.is_not(None),
            Task.due_date <= utcnow() + timedelta(days=DUE_SOON_DAYS),
        )
        .order_by(Task.due_date.asc())
        .limit(5)
    ).all()

    recent_projects = session.exec(
        select(Project)
        .where(Project.id.in_(accessible_project_ids(current_user.id)))
        .order_by(Project.updated_at.desc())
        .limit(5)
    ).all()

    return {
        "projects": {"owned": owned, "collaborating": collaborating, "total": owned + collaborating},
        "tasks": {
            "assigned": assigned_total,
            "open": sum(tasks_by_status[s] for s in OPEN_STATUSES),
            "completion_rate": completion_rate,
            "by_status": tasks_by_status,
        },
        "clients": {"total": sum(clients_by_status.values()), "by_status": clients_by_status},
        "due_soon": [enrich_task_response(task, session) for task in due_soon],
        "recent_projects": [build_project_response(project, session) for project in recent_projects],
    }
