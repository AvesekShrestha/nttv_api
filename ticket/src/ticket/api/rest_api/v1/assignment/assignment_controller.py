import re
from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession


import ticket
from ticket.application.assignment.assignment_service_interface import IAssignmentService
from ticket.application.assignment.dto.assignment_dto import AssignmentResponseDTO
from ticket.config.container import container
from ticket.infrastructure.persistence.sqlalchemy.database import get_session

from ticket.api.rest_api.v1.dependencies.authentication import get_current_user

router = APIRouter()


router.get("/{ticket_id}", response_model=list[AssignmentResponseDTO])
async def get_by_ticket(ticket_id : str, session : AsyncSession = Depends(get_session)) -> list[AssignmentResponseDTO] :
    
    container.session.override(session)
    assignment_service : IAssignmentService = container.assignment_service()

    result = await assignment_service.get_by_ticket_id(ticket_id=ticket_id)
    return result

router.get("/{assignment_id}", response_model=AssignmentResponseDTO)
async def get_by_id(assignment_id : str, session : AsyncSession = Depends(get_session)) -> AssignmentResponseDTO : 
    
    container.session.override(session)
    assignment_service : IAssignmentService = container.assignment_service()

    result = await assignment_service.get_by_id(assignment_id=assignment_id)
    return result
