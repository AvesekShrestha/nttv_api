from enum import member
from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import query

from authentication.api.rest_api.v1.dependencies.authentication import get_current_user
from authentication.api.rest_api.v1.dependencies.authorization import require_roles
from authentication.application.dto.bulk_team_request_dto import BulkTeamRequestDTO
from authentication.application.dto.team_dto import AddTeamMemberDTO, TeamCreateDTO, TeamDetailResponseDTO, TeamResponseDTO, TeamUpdateDTO
from authentication.application.dto.team_query_dto import TeamQueryDTO
from authentication.application.shared.pagination_response import PaginatedResponse
from authentication.application.team.team_service_interface import ITeamService
from authentication.infrastructure.persistence.sqlalchemy.database import get_session

from authentication.config.container import container

router = APIRouter()


@router.get("/", response_model=PaginatedResponse[TeamDetailResponseDTO])
async def get_all(query : Annotated[TeamQueryDTO, Query()], session : AsyncSession = Depends(get_session)):

    container.session.override(session)
    team_service = container.team_service()

    result = await team_service.get_all(query=query)
    return result

@router.get("/{team_id}", response_model=TeamDetailResponseDTO)
async def get_by_id(team_id: str, session : AsyncSession = Depends(get_session)):

    container.session.override(session)
    team_service = container.team_service()

    result = await team_service.get_by_id(team_id=team_id)
    return result

@router.post("/bulk", response_model=list[TeamDetailResponseDTO])
async def get_teams_bulk(
    payload: BulkTeamRequestDTO,
    session: AsyncSession = Depends(get_session),
):
    container.session.override(session)

    team_service: ITeamService = container.team_service()

    result = await team_service.get_by_ids(
        team_ids=payload.team_ids
    )
    return result

@router.post("/", response_model=TeamResponseDTO)
async def create(payload : TeamCreateDTO, session : AsyncSession = Depends(get_session), _= Depends(require_roles("admin"))):

    container.session.override(session)
    team_service : ITeamService = container.team_service()

    result = await team_service.create(payload=payload)
    return result

@router.post(("/{team_id}/member/{member_id}"), response_model=TeamDetailResponseDTO)
async def add_member(team_id : str, member_id: str, session : AsyncSession = Depends(get_session), _ = Depends(require_roles("admin"))):

    container.session.override(session)
    team_service = container.team_service()

    result = await team_service.add_team_member(team_id=team_id, user_id=member_id)
    return result

@router.delete(("/{team_id}/member/{member_id}"), response_model=TeamDetailResponseDTO)
async def remove_member(team_id : str, member_id : str, session : AsyncSession = Depends(get_session), _ = Depends(require_roles("admin")) ):

    container.session.override(session)
    team_service = container.team_service()

    result = await team_service.remove_team_member(team_id=team_id, user_id=member_id)
    return result

@router.patch("/{team_id}",response_model=TeamDetailResponseDTO)
async def update(team_id : str, payload : TeamUpdateDTO, session : AsyncSession = Depends(get_session), _ = Depends(require_roles("admin"))):

    container.session.override(session)
    team_service = container.team_service()

    result = await team_service.update(team_id=team_id, payload=payload)
    return result

@router.delete("/{team_id}", response_model=bool)
async def delete(team_id : str, session : AsyncSession = Depends(get_session), _ = Depends(require_roles("admin"))):

    container.session.override(session)
    team_service = container.team_service()

    result = await team_service.delete(team_id=team_id)
    return result
