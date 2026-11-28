from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

import ticket
from ticket.application.assignment.assignment_service_interface import IAssignmentService
from ticket.application.assignment.dto.assignment_dto import AssignmentResponseDTO, ReassignmentDTO
from ticket.application.shared.jwt_payload import JWTPayload
from ticket.application.ticket.dto.ticket_create_dto import TicketCreateDTO
from ticket.application.ticket.dto.ticket_response_dto import TicketResponseDTO
from ticket.application.ticket.dto.ticket_update_dto import TicketUpdateDTO
from ticket.application.ticket.ticket_service_interface import ITicketService
from ticket.application.shared.pagination_response_dto import PaginatedResponse
from ticket.application.ticket.dto.ticket_query_dto import TicketQueryDTO

from ticket.api.rest_api.v1.dependencies.authentication import get_current_user
from ticket.api.rest_api.v1.dependencies.authorization import require_roles

from ticket.config.container import container

from ticket.infrastructure.persistence.sqlalchemy.database import get_session

router = APIRouter()

@router.get("/", response_model=PaginatedResponse[TicketResponseDTO])
async def get_all(query : Annotated[TicketQueryDTO, Query()], session : AsyncSession = Depends(get_session)) -> PaginatedResponse[TicketResponseDTO]: 

    container.session.override(session)
    ticket_service : ITicketService = container.ticket_service()

    result = await ticket_service.get_all(query=query)
    return result

@router.get("/{ticket_id}", response_model=TicketResponseDTO)
async def get_by_id(ticket_id : str, session : AsyncSession = Depends(get_session)) -> TicketResponseDTO : 

    container.session.override(session)
    ticket_service : ITicketService = container.ticket_service()

    result = await ticket_service.get_by_id(ticket_id=ticket_id)
    return result


@router.post("/")
async def create(payload : TicketCreateDTO, session : AsyncSession = Depends(get_session), user : JWTPayload = Depends(get_current_user)) -> TicketResponseDTO :

    container.session.override(session)
    ticket_service : ITicketService = container.ticket_service()

    result = await ticket_service.create(payload=payload, user_id=user.sub)
    return result

@router.delete("/{ticket_id}", response_model=bool)
async def delete(ticket_id : str, session : AsyncSession = Depends(get_session), _ = Depends(get_current_user)) -> bool : 

    container.session.override(session)
    ticket_service : ITicketService = container.ticket_service()

    result = await ticket_service.delete(ticket_id=ticket_id)
    return result

@router.post("/{ticket_id}/acknowldege", response_model=TicketResponseDTO)
async def acknowldege(ticket_id : str, session : AsyncSession = Depends(get_session), user : JWTPayload = Depends(get_current_user), _ = Depends(require_roles("agent")))-> TicketResponseDTO:

    container.session.override(session)
    ticket_service : ITicketService = container.ticket_service()

    result = await ticket_service.acknowldege(ticket_id=ticket_id, user_id=user.sub)
    return result

@router.post("/{ticket_id}/complete", response_model=TicketResponseDTO)
async def complete(ticket_id : str, session : AsyncSession = Depends(get_session), user : JWTPayload = Depends(get_current_user)) -> TicketResponseDTO : 

    container.session.override(session)
    ticket_service : ITicketService = container.ticket_service()

    result = await ticket_service.complete(ticket_id=ticket_id, user_id=user.sub)
    return result

@router.post("/{ticket_id}/forward", response_model=AssignmentResponseDTO)
async def forward(payload : ReassignmentDTO, ticket_id : str, session : AsyncSession = Depends(get_session), user : JWTPayload = Depends(get_current_user), _ = Depends(require_roles("agent"))) -> AssignmentResponseDTO : 

    container.session.override(session)
    assignment_service : IAssignmentService = container.assignment_service()

    result = await assignment_service.forward(ticket_id=ticket_id, actor_id=user.sub, payload=payload)
    return result

@router.post("/{ticket_id}/escalate", response_model=AssignmentResponseDTO)
async def escalate(payload : ReassignmentDTO, ticket_id : str, session : AsyncSession = Depends(get_session), user : JWTPayload = Depends(get_current_user), _ = Depends(require_roles("agent"))) -> AssignmentResponseDTO : 

    container.session.override(session)
    assignment_service : IAssignmentService = container.assignment_service()

    result = await assignment_service.escalate(ticket_id=ticket_id, actor_id=user.sub, payload=payload)
    return result

@router.get("/{ticket_id}/assignments", response_model=list[AssignmentResponseDTO])
async def get_by_ticket(ticket_id : str, session : AsyncSession = Depends(get_session)) -> list[AssignmentResponseDTO] :
    
    container.session.override(session)
    assignment_service : IAssignmentService = container.assignment_service()

    result = await assignment_service.get_by_ticket_id(ticket_id=ticket_id)
    return result
