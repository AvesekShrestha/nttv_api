from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from src.application.shared.application_exception import ApplicationException
from src.domain.shared.domain_exception import DomainException


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)

        except DomainException as exc:
            return JSONResponse(
                status_code=exc.status,
                content={
                    "code": exc.code,
                    "message": exc.message
                },
            )
        except ApplicationException as exc:
            return JSONResponse(
                status_code=exc.status,
                content={
                    "code": exc.code,
                    "message": exc.message
                },
            )

        except Exception as exc:
            return JSONResponse(
                status_code=500,
                content={
                    "error": "internal_server_error",
                    "message": str(exc),
                },
            )
