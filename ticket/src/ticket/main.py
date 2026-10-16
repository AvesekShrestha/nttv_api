
from fastapi import FastAPI

from ticket.api.rest_api import router

from ticket.api.rest_api.v1.middlewares.exception_handler_middleware import ErrorHandlerMiddleware
from ticket.api.rest_api.v1.middlewares.jwt_authentication_middleware import JWTAuthenticationMiddleware

from ticket.config.container import container

app = FastAPI()

app.include_router(router, prefix="/api", )

app.add_middleware(
    JWTAuthenticationMiddleware,
    jwt_generator=container.jwt_generator()
)

app.add_middleware(
    ErrorHandlerMiddleware,
)


