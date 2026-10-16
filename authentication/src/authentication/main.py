from fastapi import FastAPI

from authentication.api.rest_api import router

from authentication.api.rest_api.v1.middlewares.exception_handler_middleware import ErrorHandlerMiddleware
from authentication.api.rest_api.v1.middlewares.jwt_authentication_middleware import JWTAuthenticationMiddleware

from authentication.config.container import container

app = FastAPI()

app.include_router(router, prefix="/api", )

app.add_middleware(
    JWTAuthenticationMiddleware,
    jwt_generator=container.jwt_generator()
)

app.add_middleware(
    ErrorHandlerMiddleware,
)


