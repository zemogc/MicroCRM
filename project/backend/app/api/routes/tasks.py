from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from typing import List
from ...models.task import Task, TaskCreate, TaskUpdate, TaskResponse
from ...models.project import Project
from ...models.user import User
from ...core.database import get_session

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

@router.get("/", response_model=List[TaskResponse])
def list_tasks(session: Session = Depends(get_session)) -> List[TaskResponse]:
    """Get all tasks"""
    statement = select(Task).order_by(Task.created_at.desc())
    tasks = session.exec(statement).all()
    return [enrich_task_response(task, session) for task in tasks]

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
def create_task(payload: TaskCreate, session: Session = Depends(get_session)) -> TaskResponse:
    """Create a new task"""
    # Validate that the project exists
    project = session.get(Project, payload.project_id)
    if not project:
        raise HTTPException(status_code=400, detail="project_id does not exist")
    
    # Validate that assigned_to user exists (if provided)
    if payload.assigned_to:
        user = session.get(User, payload.assigned_to)
        if not user:
            raise HTTPException(status_code=400, detail="assigned_to user does not exist")
    
    # For now, we'll use user ID 1 as creator. In a real app, this would come from auth
    creator = session.get(User, 1)
    if not creator:
        raise HTTPException(status_code=400, detail="Creator user not found")
    
    # Create new task
    task = Task(**payload.model_dump(), crated_by=1)
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

