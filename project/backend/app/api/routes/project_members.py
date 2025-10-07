from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from typing import List
from ...models.project_member import ProjectMember, ProjectMemberCreate, ProjectMemberUpdate, ProjectMemberResponse
from ...models.project import Project
from ...models.user import User
from ...models.role import Role
from ...core.database import get_session

router = APIRouter(prefix="/project-members", tags=["project-members"])

def create_member_response(member: ProjectMember, session: Session) -> ProjectMemberResponse:
    """Helper function to create ProjectMemberResponse with related data"""
    user = session.get(User, member.user_id)
    role = session.get(Role, member.role_id)
    added_by_user = session.get(User, member.added_by)
    
    return ProjectMemberResponse(
        **member.model_dump(),
        user_name=user.name if user else "Unknown User",
        role_name=role.name if role else "Unknown Role",
        added_by_name=added_by_user.name if added_by_user else "Unknown User"
    )

@router.get("/", response_model=List[ProjectMemberResponse])
def list_project_members(session: Session = Depends(get_session)) -> List[ProjectMemberResponse]:
    """Get all project members"""
    statement = select(ProjectMember).order_by(ProjectMember.created_at.desc())
    members = session.exec(statement).all()
    return [create_member_response(member, session) for member in members]

@router.get("/project/{project_id}", response_model=List[ProjectMemberResponse])
def list_project_members_by_project(project_id: int, session: Session = Depends(get_session)) -> List[ProjectMemberResponse]:
    """Get all members for a specific project"""
    # Validate project exists
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    statement = select(ProjectMember).where(ProjectMember.project_id == project_id).order_by(ProjectMember.created_at.desc())
    members = session.exec(statement).all()
    return [create_member_response(member, session) for member in members]

@router.get("/user/{user_id}", response_model=List[ProjectMemberResponse])
def list_project_members_by_user(user_id: int, session: Session = Depends(get_session)) -> List[ProjectMemberResponse]:
    """Get all projects where a user is a member"""
    # Validate user exists
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    statement = select(ProjectMember).where(ProjectMember.user_id == user_id).order_by(ProjectMember.created_at.desc())
    members = session.exec(statement).all()
    return [create_member_response(member, session) for member in members]

@router.post("/", response_model=ProjectMemberResponse, status_code=201)
def create_project_member(payload: ProjectMemberCreate, session: Session = Depends(get_session)) -> ProjectMemberResponse:
    """Add a user to a project with a specific role"""
    # Validate that the project exists
    project = session.get(Project, payload.project_id)
    if not project:
        raise HTTPException(status_code=400, detail="project_id does not exist")
    
    # Validate that the user exists
    user = session.get(User, payload.user_id)
    if not user:
        raise HTTPException(status_code=400, detail="user_id does not exist")
    
    # Validate that the role exists
    role = session.get(Role, payload.role_id)
    if not role:
        raise HTTPException(status_code=400, detail="role_id does not exist")
    
    # Validate that the user adding the member exists
    added_by_user = session.get(User, payload.added_by)
    if not added_by_user:
        raise HTTPException(status_code=400, detail="added_by user does not exist")
    
    # Check if user is already a member of this project
    statement = select(ProjectMember).where(
        ProjectMember.project_id == payload.project_id,
        ProjectMember.user_id == payload.user_id
    )
    existing_member = session.exec(statement).first()
    if existing_member:
        raise HTTPException(status_code=400, detail="User is already a member of this project")
    
    # Create new member
    member = ProjectMember(**payload.model_dump())
    session.add(member)
    session.commit()
    session.refresh(member)
    
    return create_member_response(member, session)

@router.get("/{member_id}", response_model=ProjectMemberResponse)
def get_project_member(member_id: int, session: Session = Depends(get_session)) -> ProjectMemberResponse:
    """Get project member by ID"""
    member = session.get(ProjectMember, member_id)
    if not member:
        raise HTTPException(status_code=404, detail="Project member not found")
    return create_member_response(member, session)

@router.put("/{member_id}", response_model=ProjectMemberResponse)
def update_project_member(member_id: int, payload: ProjectMemberUpdate, session: Session = Depends(get_session)) -> ProjectMemberResponse:
    """Update project member role"""
    member = session.get(ProjectMember, member_id)
    if not member:
        raise HTTPException(status_code=404, detail="Project member not found")
    
    # Validate that the new role exists
    role = session.get(Role, payload.role_id)
    if not role:
        raise HTTPException(status_code=400, detail="role_id does not exist")
    
    # Update member
    member.role_id = payload.role_id
    session.add(member)
    session.commit()
    session.refresh(member)
    
    return create_member_response(member, session)

@router.delete("/{member_id}", status_code=204)
def delete_project_member(member_id: int, session: Session = Depends(get_session)):
    """Remove user from project"""
    member = session.get(ProjectMember, member_id)
    if not member:
        raise HTTPException(status_code=404, detail="Project member not found")
    
    session.delete(member)
    session.commit()
    return None


