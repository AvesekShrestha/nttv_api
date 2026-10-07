from enum import member
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.rest_api.dependencies.authentication import get_current_user
from src.api.rest_api.dependencies.authorization import require_roles
from src.application.dto.team_dto import AddTeamMemberDTO, TeamCreateDTO, TeamResponseDTO, TeamUpdateDTO
from src.infrastructure.persistence.sqlalchemy.database import get_session

from src.config.container import container

router = APIRouter()


@router.get("/team", response_model=List[TeamResponseDTO])
async def get_all(session : AsyncSession = Depends(get_session), _ = Depends(get_current_user)):

    container.session.override(session)
    team_service = container.team_service()

    result = await team_service.get_all()
    return result

@router.get("/team/{team_id}", response_model=TeamResponseDTO)
async def get_by_id(team_id: str, session : AsyncSession = Depends(get_session), _ = Depends(get_current_user)):

    container.session.override(session)
    team_service = container.team_service()

    result = await team_service.get_by_id(team_id=team_id)
    return result

@router.post("/team", response_model=TeamResponseDTO)
async def create(payload : TeamCreateDTO, session : AsyncSession = Depends(get_session), _= Depends(require_roles("customer"))):

    container.session.override(session)
    team_service = container.team_service()

    result = await team_service.create(payload=payload)
    return result

@router.post(("/team/{team_id}/member/{member_id}"), response_model=TeamResponseDTO)
async def add_member(team_id : str, member_id: str, session : AsyncSession = Depends(get_session), _ = Depends(require_roles("admin"))):

    container.session.override(session)
    team_service = container.team_service()

    result = await team_service.add_team_member(team_id=team_id, user_id=member_id)
    return result

@router.post(("/team/{team_id}/member/{member_id}"), response_model=TeamResponseDTO)
async def remove_member(team_id : str, member_id : str, session : AsyncSession = Depends(get_session), _ = Depends(require_roles("admin")) ):

    container.session.override(session)
    team_service = container.team_service()

    result = await team_service.remove_team_member(team_id=team_id, user_id=member_id)
    return result

@router.patch("/team/{team_id}",response_model=TeamResponseDTO)
async def update(team_id : str, payload : TeamUpdateDTO, session : AsyncSession = Depends(get_session), _ = Depends(require_roles("admin"))):

    container.session.override(session)
    team_service = container.team_service()

    result = await team_service.update(team_id=team_id, payload=payload)
    return result

@router.delete("/team/{team_id}")
async def delete(team_id : str, session : AsyncSession = Depends(get_session), _ = Depends(require_roles("admin"))):

    container.session.override(session)
    team_service = container.team_service()

    result = await team_service.delete(team_id=team_id)
    return result


