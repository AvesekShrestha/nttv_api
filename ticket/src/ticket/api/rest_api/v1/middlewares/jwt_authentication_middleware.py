from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from ticket.application.shared.jwt_generator_interface import IJWTGenerator


class JWTAuthenticationMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, jwt_generator: IJWTGenerator):
        super().__init__(app)
        self.jwt_generator = jwt_generator

    async def dispatch(self, request: Request, call_next):
        authorization = request.headers.get("Authorization")
        if authorization:
            scheme, token = authorization.split(" ", 1)

            if scheme.lower() == "bearer":
                payload = await self.jwt_generator.verify(token)

                request.state.user = payload

        return await call_next(request)
