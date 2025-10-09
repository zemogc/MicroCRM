from fastapi import APIRouter, HTTPException, Depends, Request, Query
from sqlmodel import Session, select, func, col
from typing import List, Optional
from ...models.task import Task, TaskCreate, TaskUpdate, TaskResponse
from ...models.project import Project
from ...models.user import User
from ...models.pagination import PaginatedResponse
from ...core.database import get_session
from ...core.auth import get_current_active_user
from ...core.rate_limit import rate_limit_api
from ...core.settings import get_settings

router = APIRouter(prefix="/tasks", tags=["tasks"])

def enrich_task_response(task: Task, session: Session) -> TaskResponse:
    """Helper function to enrich task with related information"""
    # Get project information
    project = session.get(Project, task.project_id)
    
    # Get assigned user information
    assigned_user = None
    if task.assigned_to:
        assigned_user = session.get(User, task.assigned_to)
    
    # Get creator information
    creator = session.get(User, task.crated_by)
    
    # Create enriched task data
    task_data = task.model_dump()
    task_data['project_name'] = project.name if project else "Unknown Project"
    task_data['assigned_to_email'] = assigned_user.email if assigned_user else None
    task_data['created_by_email'] = creator.email if creator else "Unknown User"
    
    return TaskResponse.model_validate(task_data)

@router.get("/", response_model=PaginatedResponse[TaskResponse])
async def list_tasks(
    request: Request,
    session: Session = Depends(get_session),
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=10, ge=1, le=100, description="Number of records to return"),
    order_by: str = Query(default="created_at", description="Field to order by"),
    order_dir: str = Query(default="desc", description="Order direction (asc or desc)"),
    search: Optional[str] = Query(default=None, description="Search by title or description"),
    status: Optional[str] = Query(default=None, description="Filter by status"),
    project_id: Optional[int] = Query(default=None, description="Filter by project ID"),
    assigned_to: Optional[int] = Query(default=None, description="Filter by assigned user ID"),
    current_user: User = Depends(get_current_active_user)
) -> PaginatedResponse[TaskResponse]:
    """Get paginated list of tasks with filtering and ordering"""
    settings = get_settings()
    await rate_limit_api(request, settings.rate_limit_api_per_min, str(current_user.id))
    
    # Base query
    statement = select(Task)
    
    # Apply filters
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
    
    # Get total count
    count_statement = select(func.count()).select_from(statement.subquery())
    total = session.exec(count_statement).one()
    
    # Apply ordering
    order_column = getattr(Task, order_by, Task.created_at)
    if order_dir.lower() == "asc":
        statement = statement.order_by(col(order_column).asc())
    else:
        statement = statement.order_by(col(order_column).desc())
    
    # Apply pagination
    statement = statement.offset(skip).limit(limit)
    
    # Execute query
    tasks = session.exec(statement).all()
    
    return PaginatedResponse(
        items=[enrich_task_response(task, session) for task in tasks],
        total=total,
        skip=skip,
        limit=limit,
        has_more=(skip + limit) < total
    )

@router.get("/project/{project_id}", response_model=List[TaskResponse])
def list_tasks_by_project(project_id: int, session: Session = Depends(get_session)) -> List[TaskResponse]:
    """Get all tasks for a specific project"""
    # Validate project exists
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    statement = select(Task).where(Task.project_id == project_id).order_by(Task.created_at.desc())
    tasks = session.exec(statement).all()
    return [enrich_task_response(task, session) for task in tasks]

@router.post("/", response_model=TaskResponse, status_code=201)
async def create_task(
    request: Request,
    payload: TaskCreate, 
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
) -> TaskResponse:
    """Create a new task"""
    settings = get_settings()
    await rate_limit_api(request, settings.rate_limit_api_per_min, str(current_user.id))
    
    # Validate that the project exists
    project = session.get(Project, payload.project_id)
    if not project:
        raise HTTPException(status_code=400, detail="project_id does not exist")
    
    # Validate that assigned_to user exists (if provided)
    if payload.assigned_to:
        user = session.get(User, payload.assigned_to)
        if not user:
            raise HTTPException(status_code=400, detail="assigned_to user does not exist")
    
    # Create new task with current user as creator
    task = Task(**payload.model_dump(), crated_by=current_user.id)
    session.add(task)
    session.commit()
    session.refresh(task)
    return enrich_task_response(task, session)

@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, session: Session = Depends(get_session)) -> TaskResponse:
    """Get task by ID"""
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return enrich_task_response(task, session)

@router.put("/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, payload: TaskUpdate, session: Session = Depends(get_session)) -> TaskResponse:
    """Update task by ID"""
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Validate assigned_to user exists (if being updated)
    if payload.assigned_to:
        user = session.get(User, payload.assigned_to)
        if not user:
            raise HTTPException(status_code=400, detail="assigned_to user does not exist")
    
    # Update task
    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)
    
    session.add(task)
    session.commit()
    session.refresh(task)
    return enrich_task_response(task, session)

@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: int, session: Session = Depends(get_session)):
    """Delete task by ID"""
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    session.delete(task)
    session.commit()
    return None

@router.get("/user/{user_id}", response_model=List[TaskResponse])
def list_tasks_by_user(user_id: int, session: Session = Depends(get_session)) -> List[TaskResponse]:
    """Get all tasks assigned to a specific user"""
    # Validate user exists
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    statement = select(Task).where(Task.assigned_to == user_id).order_by(Task.created_at.desc())
    tasks = session.exec(statement).all()
    return [enrich_task_response(task, session) for task in tasks]

