from fastapi import APIRouter

from .auth.auth_controller import router as auth_router
from .category.category_controller import router as category_router
from .team.team_controller import router as team_router
from .user.user_controller import router as user_router

router = APIRouter()

router.include_router(auth_router, prefix="/auth")
router.include_router(category_router, prefix="/category")
router.include_router(team_router, prefix="/team")
router.include_router(user_router, prefix="/user")
