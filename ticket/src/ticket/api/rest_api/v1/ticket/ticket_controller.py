from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.engine import result
from sqlalchemy.ext.asyncio import AsyncSession

import ticket
from ticket.application.assignment.assignment_service_interface import IAssignmentService
from ticket.application.assignment.dto.assignment_dto import AssignmentResponseDTO, ReassignmentDTO
from ticket.application.ticket import ticket_service
from ticket.application.ticket.dto.ticket_create_dto import TicketCreateDTO
from ticket.application.ticket.dto.ticket_response_dto import TicketResponseDTO
from ticket.application.ticket.dto.ticket_update_dto import TicketUpdateDTO
from ticket.application.ticket.ticket_service_interface import ITicketService

from ticket.api.rest_api.v1.dependencies.authentication import get_current_user

from ticket.config.container import container


from ticket.infrastructure.persistence.sqlalchemy.database import get_session

router = APIRouter()

@router.get("/", response_model=list[TicketResponseDTO])
async def get_all(self, session : AsyncSession = Depends(get_session), page : Optional[int] = None, limit : Optional[int] = None) -> list[TicketResponseDTO]: 

    ticket_service : ITicketService = container.ticket_service()
    container.session.override(session)

    result = await ticket_service.get_all(page=page, limit=limit)
    return result

@router.get("/{ticket_id}", response_model=TicketResponseDTO)
async def get_by_id(self, ticket_id : str, session : AsyncSession = Depends(get_session)) -> TicketResponseDTO : 

    ticket_service : ITicketService = container.ticket_service()
    container.session.override(session)

    result = await ticket_service.get_by_id(ticket_id=ticket_id)
    return result


@router.post("/")
async def create(self, payload : TicketCreateDTO, session : AsyncSession = Depends(get_session), user_id : str = Depends(get_current_user)) -> TicketResponseDTO :

    ticket_service : ITicketService = container.ticket_service()
    container.session.override(session)

    result = await ticket_service.create(payload=payload, user_id=user_id)
    return result

@router.delete("/{ticket_id}", response_model=bool)
async def delete(self, ticket_id : str, session : AsyncSession = Depends(get_session), _ = Depends(get_current_user)) -> bool : 

    ticket_service : ITicketService = container.ticket_service()
    container.session.override(session)

    result = await ticket_service.delete(ticket_id=ticket_id)
    return result

@router.post("/{ticket_id}/acknowldege", response_model=TicketResponseDTO)
async def acknowldege(ticket_id : str, session : AsyncSession = Depends(get_session), user_id : str = Depends(get_current_user))-> TicketResponseDTO:

    ticket_service : ITicketService = container.ticket_service()
    container.session.override(session)

    result = await ticket_service.acknowldege(ticket_id=ticket_id, user_id=user_id)
    return result

@router.post("/{ticket_id}/complete", response_model=TicketResponseDTO)
async def complete(ticket_id : str, session : AsyncSession = Depends(get_session), user_id : str = Depends(get_current_user)) -> TicketResponseDTO : 

    ticket_service : ITicketService = container.ticket_service()
    container.session.override(session)

    result = await ticket_service.complete(ticket_id=ticket_id, user_id=user_id)
    return result

router.post("/{ticket_id}/forward", response_model=AssignmentResponseDTO)
async def forward(payload : ReassignmentDTO, ticket_id : str, session : AsyncSession = Depends(get_session), user_id : str = Depends(get_current_user)) -> AssignmentResponseDTO : 

    container.session.override(session)
    assignment_service : IAssignmentService = container.assignment_service()

    result = await assignment_service.forward(ticket_id=ticket_id, actor_id=user_id, payload=payload)
    return result

router.post("/{ticket_id}/escalate", response_model=AssignmentResponseDTO)
async def escalate(payload : ReassignmentDTO, ticket_id : str, session : AsyncSession = Depends(get_session), user_id : str = Depends(get_current_user)) -> AssignmentResponseDTO : 

    container.session.override(session)
    assignment_service : IAssignmentService = container.assignment_service()

    result = await assignment_service.escalate(ticket_id=ticket_id, actor_id=user_id, payload=payload)
    return result
