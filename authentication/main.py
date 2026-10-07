from fastapi import FastAPI

from src.api.rest_api.controllers.auth_controller import router as auth_router
from src.api.rest_api.controllers.category_controller import router as category_router
from src.api.rest_api.controllers.team_controller import router as team_router

from src.api.rest_api.middlewares.exception_handler_middleware import ErrorHandlerMiddleware
from src.api.rest_api.middlewares.jwt_authentication_middleware import JWTAuthenticationMiddleware

from src.config.container import container

app = FastAPI()

app.include_router(auth_router, prefix="/api", )
app.include_router(category_router, prefix="/api", )
app.include_router(team_router, prefix="/api", )

app.add_middleware(
    JWTAuthenticationMiddleware,
    jwt_generator=container.jwt_generator()
)

app.add_middleware(
    ErrorHandlerMiddleware,
)


