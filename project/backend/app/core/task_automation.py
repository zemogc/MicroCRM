"""
Task Automation Module
=====================
Handles automatic task status updates based on business rules.
"""

from sqlmodel import Session, select, func
from ..models.task import Task
from .clock import utcnow

# ONLY pending and in_progress tasks can be automatically marked as overdue.
# Tasks in 'in_review', 'completed', 'cancelled', or already 'overdue' are left as they are.
AUTO_OVERDUE_STATUSES = ["pending", "in_progress"]


def _overdue_filter():
    return (
        Task.due_date.is_not(None),  # Has due date
        Task.due_date < utcnow(),  # Due date has passed
        Task.status.in_(AUTO_OVERDUE_STATUSES),
    )


def update_overdue_tasks(session: Session) -> int:
    """
    Update tasks to 'overdue' status if their due_date has passed
    and they are ONLY in 'pending' or 'in_progress' status.

    Returns:
        Number of tasks updated
    """
    overdue_tasks = session.exec(select(Task).where(*_overdue_filter())).all()

    for task in overdue_tasks:
        task.status = "overdue"

    if overdue_tasks:
        session.commit()

    return len(overdue_tasks)


def get_overdue_tasks_count(session: Session) -> int:
    """
    Get count of tasks that should be overdue but aren't marked yet.
    ONLY counts tasks in 'pending' or 'in_progress' status.
    """
    return session.exec(select(func.count()).select_from(Task).where(*_overdue_filter())).one()
