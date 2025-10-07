from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from typing import List
from ...models.project import Project, ProjectCreate, ProjectUpdate, ProjectResponse
from ...models.user import User
from ...core.database import get_session

router = APIRouter(prefix="/projects", tags=["projects"])

@router.get("/", response_model=List[ProjectResponse])
def list_projects(session: Session = Depends(get_session)) -> List[ProjectResponse]:
    """Get all projects"""
    statement = select(Project).order_by(Project.updated_at.desc())
    projects = session.exec(statement).all()
    
    # Create response with creator names
    result = []
    for project in projects:
        creator = session.get(User, project.crated_by)
        project_data = project.model_dump()
        project_data['creator_email'] = creator.email if creator else "Unknown User"
        result.append(ProjectResponse.model_validate(project_data))
    
    return result

@router.post("/", response_model=ProjectResponse, status_code=201)
def create_project(payload: ProjectCreate, session: Session = Depends(get_session)) -> ProjectResponse:
    """Create a new project"""
    # Validate that the creator user exists
    user = session.get(User, payload.crated_by)
    if not user:
        raise HTTPException(status_code=400, detail="crated_by user does not exist")
    
    # Create new project
    project = Project(**payload.model_dump())
    session.add(project)
    session.commit()
    session.refresh(project)
    
    # Include creator name in response
    project_data = project.model_dump()
    project_data['creator_email'] = user.email
    
    return ProjectResponse.model_validate(project_data)

@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: int, session: Session = Depends(get_session)) -> ProjectResponse:
    """Get project by ID"""
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Include creator name
    creator = session.get(User, project.crated_by)
    project_data = project.model_dump()
    project_data['creator_email'] = creator.email if creator else "Unknown User"
    
    return ProjectResponse.model_validate(project_data)

@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(project_id: int, payload: ProjectUpdate, session: Session = Depends(get_session)) -> ProjectResponse:
    """Update project by ID"""
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Update project
    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(project, key, value)
    
    session.add(project)
    session.commit()
    session.refresh(project)
    
    # Include creator name in response
    creator = session.get(User, project.crated_by)
    project_data = project.model_dump()
    project_data['creator_email'] = creator.email if creator else "Unknown User"
    
    return ProjectResponse.model_validate(project_data)

@router.delete("/{project_id}", status_code=204)
def delete_project(project_id: int, session: Session = Depends(get_session)):
    """Delete project by ID"""
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    session.delete(project)
    session.commit()
    return None
