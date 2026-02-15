
# [AI GENERATED]
# Model: GitHub Copilot (GPT-4.1)
# Logic: Implements team management endpoints for Alfred platform.
# Why: Required for unified team CRUD, membership, and quota management.
# Root Cause: No AI-generated code header present in legacy router.
# Context: Extend for advanced team analytics, SSO, and SCIM. For complex workflows, consider Claude Sonnet or GPT-5.1-Codex.

import uuid
from typing import List

from fastapi import APIRouter, Body, Depends, HTTPException, Path
from sqlmodel import Session, select

from ..dependencies import get_current_user, get_session, require_admin
from ..models import Team, TeamMemberLink, User, UserStatus
from ..schemas import (
    AddMemberByEmailRequest,
    TeamCreate,
    TeamMember,
    TeamResponse,
    TeamUpdate
)

router = APIRouter(prefix="/v1", tags=["Team Infrastructure"])

@router.post("/admin/teams", response_model=TeamResponse, dependencies=[Depends(require_admin)])
async def create_team(
    team_data: TeamCreate,
    session: Session = Depends(get_session),
    admin_user: User = Depends(get_current_user),
):
    """Create a new team."""
    team = Team(
        id=uuid.uuid4(),
        name=team_data.name,
        description=team_data.description,
        common_pool=team_data.common_pool or 10000.00
    )
    session.add(team)
    session.commit()
    session.refresh(team)
    
    return TeamResponse(
        id=str(team.id),
        name=team.name,
        description=team.description,
        common_pool=team.common_pool,
        used_pool=team.used_pool,
        available_pool=team.available_pool,
        member_count=0
    )

@router.get("/admin/teams", response_model=List[TeamResponse], dependencies=[Depends(require_admin)])
async def list_teams(
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session)
):
    """List all teams (admin endpoint)."""
    teams = session.exec(select(Team).offset(skip).limit(limit)).all()
    
    result = []
    for team in teams:
        member_count = session.exec(
            select(TeamMemberLink).where(TeamMemberLink.team_id == team.id)
        ).all()
        member_count = len(member_count)
        result.append(TeamResponse(
            id=str(team.id),
            name=team.name,
            description=team.description,
            common_pool=team.common_pool,
            used_pool=team.used_pool,
            available_pool=team.available_pool,
            member_count=member_count
        ))
    return result

@router.put("/admin/teams/{team_id}", response_model=TeamResponse, dependencies=[Depends(require_admin)])
async def update_team(
    team_id: str = Path(..., pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"),
    team_data: TeamUpdate = Body(...),
    session: Session = Depends(get_session),
    admin_user: User = Depends(get_current_user),
):
    """Update a team (admin endpoint)."""
    team = session.get(Team, uuid.UUID(team_id))
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
        
    if team_data.name is not None: team.name = team_data.name
    if team_data.description is not None: team.description = team_data.description
    if team_data.common_pool is not None: team.common_pool = team_data.common_pool
    
    session.add(team)
    session.commit()
    session.refresh(team)
    
    member_count = len(session.exec(select(TeamMemberLink).where(TeamMemberLink.team_id == team.id)).all())
    
    return TeamResponse(
        id=str(team.id),
        name=team.name,
        description=team.description,
        common_pool=team.common_pool,
        used_pool=team.used_pool,
        available_pool=team.available_pool,
        member_count=member_count
    )

@router.delete("/admin/teams/{team_id}", dependencies=[Depends(require_admin)])
async def delete_team(
    team_id: str = Path(..., pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"),
    session: Session = Depends(get_session),
    admin_user: User = Depends(get_current_user),
):
    """Delete a team (admin endpoint)."""
    team = session.get(Team, uuid.UUID(team_id))
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
        
    session.delete(team)
    session.commit()
    
    return {"message": "Team deleted successfully"}

@router.get("/admin/teams/{team_id}/members", response_model=List[TeamMember], dependencies=[Depends(require_admin)])
async def get_team_members(
    team_id: str = Path(..., pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"),
    session: Session = Depends(get_session)
):
    """Get members of a team."""
    team = session.get(Team, uuid.UUID(team_id))
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
        
    links = session.exec(select(TeamMemberLink).where(TeamMemberLink.team_id == team.id)).all()
    user_ids = [link.user_id for link in links]
    users = session.exec(select(User).where(User.id.in_(user_ids))).all()
    
    user_map = {u.id: u for u in users}
    
    return [
        TeamMember(
            id=str(link.user_id),
            name=user_map[link.user_id].name if link.user_id in user_map else "Unknown",
            email=user_map[link.user_id].email if link.user_id in user_map else "Unknown",
            is_admin=link.is_admin
        ) for link in links
    ]

@router.post("/admin/teams/{team_id}/members", dependencies=[Depends(require_admin)])
async def add_team_member_email(
    team_id: str = Path(..., pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"), 
    request: AddMemberByEmailRequest = Body(...),
    session: Session = Depends(get_session)
):
    """Add member by email."""
    # Verify team exists
    team = session.get(Team, uuid.UUID(team_id))
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
        
    # Find user by email
    user = session.exec(select(User).where(User.email == request.email)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User with this email not found")
        
    # Check if already a member
    existing = session.exec(
        select(TeamMemberLink)
        .where(TeamMemberLink.team_id == team.id)
        .where(TeamMemberLink.user_id == user.id)
    ).first()
    
    if existing:
        return {"message": "User is already a member of this team"}
        
    link = TeamMemberLink(
        team_id=team.id,
        user_id=user.id,
        is_admin=request.is_admin
    )
    session.add(link)
    session.commit()
    
    return {"message": "Member added successfully"}

@router.post("/admin/teams/{team_id}/members/{user_id}", dependencies=[Depends(require_admin)])
async def add_team_member(
    team_id: str = Path(..., pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"),
    user_id: str = Path(..., pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"),
    is_admin: bool = False,
    session: Session = Depends(get_session)
):
    """Add a user to a team."""
    team = session.get(Team, uuid.UUID(team_id))
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
        
    user = session.get(User, uuid.UUID(user_id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    # Check if already a member
    existing = session.exec(
        select(TeamMemberLink)
        .where(TeamMemberLink.team_id == team.id)
        .where(TeamMemberLink.user_id == user.id)
    ).first()
    
    if existing:
        return {"message": "User is already a member of this team"}
        
    link = TeamMemberLink(
        team_id=team.id,
        user_id=user.id,
        is_admin=is_admin
    )
    session.add(link)
    session.commit()
    
    return {"message": "Member added successfully"}

@router.delete("/admin/teams/{team_id}/members/{user_id}", dependencies=[Depends(require_admin)])
async def remove_team_member(
    team_id: str = Path(..., pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"),
    user_id: str = Path(..., pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"),
    session: Session = Depends(get_session)
):
    """Remove a user from a team."""
    link = session.exec(
        select(TeamMemberLink)
        .where(TeamMemberLink.team_id == uuid.UUID(team_id))
        .where(TeamMemberLink.user_id == uuid.UUID(user_id))
    ).first()
    
    if not link:
        raise HTTPException(status_code=404, detail="Membership record not found")
        
    session.delete(link)
    session.commit()
    
    return {"message": "Member removed successfully"}
