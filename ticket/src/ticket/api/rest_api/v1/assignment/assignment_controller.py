import re
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ticket.application.assignment.assignment_service_interface import IAssignmentService
from ticket.application.assignment.dto.assignment_dto import AssignmentResponseDTO
from ticket.application.assignment.dto.assignment_query_dto import AssignmentQueryDTO
from ticket.application.assignment.dto.claim_eligibility_dto import ClaimEligibilityResponse
from ticket.application.shared.pagination_response_dto import PaginatedResponse
from ticket.application.shared.jwt_payload import JWTPayload

from ticket.config.container import container
from ticket.infrastructure.persistence.sqlalchemy.database import get_session

from ticket.api.rest_api.v1.dependencies.authentication import get_current_user

router = APIRouter()

@router.get("/{assignment_id}", response_model=AssignmentResponseDTO)
async def get_by_id(assignment_id : str, session : AsyncSession = Depends(get_session)) -> AssignmentResponseDTO : 
    
    container.session.override(session)
    assignment_service : IAssignmentService = container.assignment_service()

    result = await assignment_service.get_by_id(assignment_id=assignment_id)
    return result


@router.get("/", response_model=PaginatedResponse[AssignmentResponseDTO])
async def get_all(query : Annotated[AssignmentQueryDTO, Query()], session : AsyncSession = Depends(get_session)) :

    container.session.override(session)
    assignment_service : IAssignmentService = container.assignment_service()

    result = await assignment_service.get_all(query=query)
    return result

@router.get("/{assignment_id}/claim-eligibility", response_model=ClaimEligibilityResponse)
async def claim_eligibility(assignment_id : str, session : AsyncSession = Depends(get_session), user : JWTPayload = Depends(get_current_user)) : 

    container.session.override(session)
    assignment_service : IAssignmentService = container.assignment_service()

    result = await assignment_service.claim_eligibility(
        assignment_id=assignment_id,
        agent_id=user.sub
    )
    return result
