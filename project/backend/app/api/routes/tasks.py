from fastapi import APIRouter, HTTPException, Query
from sqlmodel import Session, select
from typing import List, Optional
from ...models.task import Task, TaskCreate, TaskUpdate, TaskResponse
from ...models.project import Project
from ...models.user import User
from ...models.pagination import PaginatedResponse
from ...core.auth import CurrentUser, SessionDep
from ...core.clock import utcnow
from ...core.permissions import (
    accessible_project_ids,
    ensure_self,
    get_accessible_project,
    get_owned_project,
    is_project_member,
)
from ...core.query import apply_ordering, count_rows
from ...core.task_automation import update_overdue_tasks, get_overdue_tasks_count

router = APIRouter(prefix="/tasks", tags=["tasks"])

def enrich_task_response(task: Task, session: Session) -> TaskResponse:
    """Helper function to enrich task with related information"""
    project = session.get(Project, task.project_id)
    assigned_user = session.get(User, task.assigned_to) if task.assigned_to else None

    task_data = task.model_dump()
    task_data['project_name'] = project.name if project else "Unknown Project"
    task_data['project_description'] = project.description if project else None
    task_data['assigned_to_name'] = assigned_user.name if assigned_user else None
    task_data['assigned_to_email'] = assigned_user.email if assigned_user else None

    return TaskResponse.model_validate(task_data)

def validate_assignee(session: Session, project: Project, user_id: Optional[int]) -> None:
    """Tasks can only be assigned to the owner or collaborators of the project"""
    if user_id is None:
        return
    if not session.get(User, user_id):
        raise HTTPException(status_code=400, detail="assigned_to user does not exist")
    if not is_project_member(session, project, user_id):
        raise HTTPException(status_code=400, detail="assigned_to user is not a member of the project")

def get_task_or_404(session: Session, task_id: int, current_user: User) -> tuple[Task, Project]:
    """Task and its project, hidden (404) if the user has no access to the project"""
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    project = session.get(Project, task.project_id)
    if not project or not is_project_member(session, project, current_user.id):
        raise HTTPException(status_code=404, detail="Task not found")
    return task, project

@router.get("/", response_model=PaginatedResponse[TaskResponse])
def list_tasks(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=10, ge=1, le=100, description="Number of records to return"),
    order_by: str = Query(default="created_at", description="Field to order by"),
    order_dir: str = Query(default="desc", description="Order direction (asc or desc)"),
    search: Optional[str] = Query(default=None, description="Search by title or description"),
    status: Optional[str] = Query(default=None, description="Filter by status"),
    project_id: Optional[int] = Query(default=None, description="Filter by project ID"),
    assigned_to: Optional[int] = Query(default=None, description="Filter by assigned user ID"),
) -> PaginatedResponse[TaskResponse]:
    """Tasks of the projects the current user can see, with filtering and ordering"""
    statement = select(Task).where(Task.project_id.in_(accessible_project_ids(current_user.id)))

    if search:
        search_filter = f"%{search}%"
        statement = statement.where(
            (Task.title.like(search_filter)) | (Task.description.like(search_filter))
        )

    if status:
        statement = statement.where(Task.status == status)

    if project_id is not None:
        statement = statement.where(Task.project_id == project_id)

    if assigned_to is not None:
        statement = statement.where(Task.assigned_to == assigned_to)

    total = count_rows(session, statement)
    statement = apply_ordering(statement, Task, order_by, order_dir, default="created_at")
    tasks = session.exec(statement.offset(skip).limit(limit)).all()

    return PaginatedResponse(
        items=[enrich_task_response(task, session) for task in tasks],
        total=total,
        skip=skip,
        limit=limit,
        has_more=(skip + limit) < total
    )

# Static paths are declared before /{task_id} so they are not captured by it

@router.post("/update-overdue")
def update_overdue_tasks_endpoint(session: SessionDep, current_user: CurrentUser) -> dict:
    """Update tasks to overdue status if their due date has passed"""
    updated_count = update_overdue_tasks(session)
    return {
        "message": f"Successfully updated {updated_count} tasks to overdue status",
        "updated_count": updated_count,
        "timestamp": utcnow().isoformat()
    }

@router.get("/overdue-count")
def get_overdue_count(session: SessionDep, current_user: CurrentUser) -> dict:
    """Get count of tasks that should be marked as overdue"""
    return {
        "overdue_count": get_overdue_tasks_count(session),
        "timestamp": utcnow().isoformat()
    }

@router.get("/project/{project_id}", response_model=List[TaskResponse])
def list_tasks_by_project(project_id: int, session: SessionDep, current_user: CurrentUser) -> List[TaskResponse]:
    """Get all tasks for a specific project (owner or collaborator)"""
    get_accessible_project(session, project_id, current_user)

    # Auto-update overdue tasks before returning
    update_overdue_tasks(session)

    statement = select(Task).where(Task.project_id == project_id).order_by(Task.created_at.desc())
    tasks = session.exec(statement).all()
    return [enrich_task_response(task, session) for task in tasks]

@router.get("/user/{user_id}", response_model=List[TaskResponse])
def list_tasks_by_user(user_id: int, session: SessionDep, current_user: CurrentUser) -> List[TaskResponse]:
    """Get all tasks assigned to the current user"""
    ensure_self(current_user, user_id)

    # Auto-update overdue tasks before returning
    update_overdue_tasks(session)

    statement = select(Task).where(Task.assigned_to == user_id).order_by(Task.created_at.desc())
    tasks = session.exec(statement).all()
    return [enrich_task_response(task, session) for task in tasks]

@router.post("/", response_model=TaskResponse, status_code=201)
def create_task(payload: TaskCreate, session: SessionDep, current_user: CurrentUser) -> TaskResponse:
    """Create a new task (project owner only)"""
    project = get_owned_project(session, payload.project_id, current_user)
    validate_assignee(session, project, payload.assigned_to)

    task = Task(**payload.model_dump())
    session.add(task)
    session.commit()
    session.refresh(task)
    return enrich_task_response(task, session)

@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, session: SessionDep, current_user: CurrentUser) -> TaskResponse:
    """Get task by ID"""
    task, _ = get_task_or_404(session, task_id, current_user)
    return enrich_task_response(task, session)

@router.put("/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, payload: TaskUpdate, session: SessionDep, current_user: CurrentUser) -> TaskResponse:
    """
    Update task by ID.
    The project owner can change every field; the assigned collaborator can only change the status.
    """
    task, project = get_task_or_404(session, task_id, current_user)
    update_data = payload.model_dump(exclude_unset=True)

    if project.id_user != current_user.id:
        if task.assigned_to != current_user.id:
            raise HTTPException(status_code=403, detail="Only the owner or the assigned user can update this task")
        if set(update_data) - {"status"}:
            raise HTTPException(status_code=403, detail="Collaborators can only change the task status")

    if "assigned_to" in update_data:
        validate_assignee(session, project, update_data["assigned_to"])

    for key, value in update_data.items():
        setattr(task, key, value)

    session.add(task)
    session.commit()
    session.refresh(task)
    return enrich_task_response(task, session)

@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: int, session: SessionDep, current_user: CurrentUser):
    """Delete task by ID (project owner only)"""
    task, project = get_task_or_404(session, task_id, current_user)
    if project.id_user != current_user.id:
        raise HTTPException(status_code=403, detail="Only the project owner can perform this action")

    session.delete(task)
    session.commit()
    return None
