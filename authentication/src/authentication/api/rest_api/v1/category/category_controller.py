from typing import Annotated, List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import query

from authentication.api.rest_api.v1.dependencies.authentication import get_current_user
from authentication.api.rest_api.v1.dependencies.authorization import require_roles
from authentication.application.dto.category_dto import CategoryResponseDTO, CategoryCreateDTO, CategoryUpdateDTO

from authentication.application.dto.category_query_dto import CategoryQueryDTO
from authentication.application.shared.pagination_response import PaginatedResponse
from authentication.infrastructure.persistence.sqlalchemy.database import get_session

from authentication.config.container import  container

router = APIRouter()

@router.get("/", response_model=PaginatedResponse[CategoryResponseDTO])
async def get_all(query : Annotated[CategoryQueryDTO, Query()] ,session : AsyncSession = Depends(get_session)):

    container.session.override(session)
    category_service = container.category_service()

    result = await category_service.get_all(query=query)
    return result

@router.get("/{category_id}", response_model=CategoryResponseDTO)
async def get_by_id(category_id : str, session : AsyncSession = Depends(get_session)):

    container.session.override(session)
    category_service = container.category_service()

    result = await category_service.get_by_id(category_id=category_id)
    return result

@router.post("/", response_model=CategoryResponseDTO)
async def create(payload : CategoryCreateDTO, session : AsyncSession = Depends(get_session), _ = Depends(require_roles("admin"))):
    
    container.session.override(session)
    category_service = container.category_service()

    result = await category_service.create(payload=payload)
    return result


@router.patch("/{category_id}", response_model=CategoryResponseDTO)
async def update(category_id : str, payload : CategoryUpdateDTO, session : AsyncSession = Depends(get_session), _ = Depends(require_roles("admin"))):

    container.session.override(session)
    category_service = container.category_service()

    result = await category_service.update(category_id=category_id, payload=payload)
    return result

@router.delete("/{category_id}", response_model=bool)
async def delete(category_id : str, session : AsyncSession = Depends(get_session), _ = Depends(require_roles("admin"))):

    container.session.override(session)
    category_service = container.category_service()

    result = await category_service.delete(category_id=category_id)
    return result
