from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.rest_api.dependencies.authentication import get_current_user

from src.api.rest_api.dependencies.authorization import require_roles
from src.application.dto.category_dto import CategoryResponseDTO, CategoryCreateDTO, CategoryUpdateDTO

from src.infrastructure.persistence.sqlalchemy.database import get_session

from src.config.container import  container

router = APIRouter()

@router.get("/category", response_model=List[CategoryResponseDTO])
async def get_all(session : AsyncSession = Depends(get_session), _ = Depends(get_current_user)):

    container.session.override(session)
    category_service = container.category_service()

    result = await category_service.get_all()
    return result

@router.get("/category/{category_id}", response_model=CategoryResponseDTO)
async def get_by_id(category_id : str, session : AsyncSession = Depends(get_session), _ = Depends(get_current_user)):

    container.session.override(session)
    category_service = container.category_service()

    result = await category_service.get_by_id(category_id=category_id)
    return result

@router.post("/category", response_model=CategoryResponseDTO)
async def create(payload : CategoryCreateDTO, session : AsyncSession = Depends(get_session), _ = Depends(require_roles("admin"))):
    
    container.session.override(session)
    category_service = container.category_service()

    result = await category_service.create(payload=payload)
    return result


@router.patch("/category/{category_id}", response_model=CategoryResponseDTO)
async def update(category_id : str, payload : CategoryUpdateDTO, session : AsyncSession = Depends(get_session), _ = Depends(require_roles("admin"))):

    container.session.override(session)
    category_service = container.category_service()

    result = await category_service.update(category_id=category_id, payload=payload)
    return result

@router.delete("/category/{category_id}")
async def delete(category_id : str, session : AsyncSession = Depends(get_session), _ = Depends(require_roles("admin"))):

    container.session.override(session)
    category_service = container.category_service()

    result = await category_service.delete(category_id=category_id)
    return result
