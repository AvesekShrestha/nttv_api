from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import session

from authentication.api.rest_api.v1.dependencies.authorization import require_roles
from authentication.application.dto.create_staff_dto import CreateStaffDTO
from authentication.application.dto.user_response_dto import UserResponseDTO
from authentication.api.rest_api.v1.dependencies.authentication import get_current_user
from authentication.application.user import user_service
from authentication.config import container
from authentication.infrastructure.persistence.sqlalchemy.database import get_session

from authentication.config.container import container

router = APIRouter()


@router.get("/me", response_model=UserResponseDTO)
async def me(current_user_id : str = Depends(get_current_user), session : AsyncSession = Depends(get_session)) :

    container.session.override(session)
    user_service = container.user_service()

    result = await user_service.get_by_id(user_id=current_user_id)
    return result

@router.get("/{user_id}", response_model=UserResponseDTO)
async def get_by_id(user_id : str, session : AsyncSession = Depends(get_session), _ = Depends(get_current_user)):
    container.session.override(session)
    user_service = container.user_service()

    result = await user_service.get_by_id(user_id=user_id)
    return result

@router.get("/", response_model=list[UserResponseDTO])
async def get_all(session : AsyncSession = Depends(get_session), _ = Depends(get_current_user)) : 
    container.session.override(session)
    user_service = container.user_service()

    result = await user_service.get_all()
    return result

@router.post("/", response_model=UserResponseDTO)
async def create_staff(payload : CreateStaffDTO, session : AsyncSession = Depends(get_session), _ = Depends(require_roles("admin"))) : 
    container.session.override(session)
    user_service = container.user_service()

    result = await user_service.create_staff(payload=payload)
    return result














