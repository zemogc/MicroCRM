"""
Task Automation Module
=====================
Handles automatic task status updates based on business rules.
"""

from sqlmodel import Session, select
from datetime import datetime
from typing import List
from ..models.task import Task
from .database import get_session


def update_overdue_tasks(session: Session) -> int:
    """
    Update tasks to 'overdue' status if their due_date has passed
    and they are ONLY in 'pending' or 'in_progress' status.
    
    Tasks in 'in_review', 'completed', 'cancelled', or already 'overdue' 
    will NOT be automatically updated.
    
    Args:
        session: Database session
        
    Returns:
        Number of tasks updated
    """
    current_time = datetime.utcnow()
    
    # Find tasks that should be marked as overdue
    # ONLY pending and in_progress tasks can be automatically marked as overdue
    statement = select(Task).where(
        Task.due_date.is_not(None),  # Has due date
        Task.due_date < current_time,  # Due date has passed
        Task.status.in_(["pending", "in_progress"])  # ONLY these statuses
    )
    
    overdue_tasks = session.exec(statement).all()
    
    # Update status to overdue
    updated_count = 0
    for task in overdue_tasks:
        task.status = "overdue"
        updated_count += 1
    
    if updated_count > 0:
        session.commit()
    
    return updated_count


def get_overdue_tasks_count(session: Session) -> int:
    """
    Get count of tasks that should be overdue but aren't marked yet.
    ONLY counts tasks in 'pending' or 'in_progress' status.
    
    Args:
        session: Database session
        
    Returns:
        Number of tasks that should be overdue
    """
    current_time = datetime.utcnow()
    
    statement = select(Task).where(
        Task.due_date.is_not(None),
        Task.due_date < current_time,
        Task.status.in_(["pending", "in_progress"])  # ONLY these statuses
    )
    
    overdue_tasks = session.exec(statement).all()
    return len(overdue_tasks)


def mark_task_overdue_if_needed(session: Session, task: Task) -> bool:
    """
    Check if a specific task should be marked as overdue and update it.
    
    Args:
        session: Database session
        task: Task to check
        
    Returns:
        True if task was updated, False otherwise
    """
    if not task.due_date:
        return False
        
    if task.status in ["completed", "cancelled", "overdue"]:
        return False
        
    current_time = datetime.utcnow()
    
    if task.due_date < current_time:
        task.status = "overdue"
        session.commit()
        return True
        
    return False
