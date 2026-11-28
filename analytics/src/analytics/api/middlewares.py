from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from analytics.domain.shared.domain_exception import DomainException
from analytics.application.shared.application_exception import ApplicationException


def setup_exception_handlers(app: FastAPI) -> None:

    @app.exception_handler(DomainException)
    async def domain_exception_handler(request: Request, exc: DomainException):
        return JSONResponse(
            status_code=exc.status,
            content={
                "error": {
                    "code": getattr(exc, "code", "DOMAIN_EXCEPTION"),
                    "message": exc.message,
                }
            },
        )

    @app.exception_handler(ApplicationException)
    async def application_exception_handler(
        request: Request, exc: ApplicationException
    ):
        return JSONResponse(
            status_code=exc.status,
            content={
                "error": {
                    "code": getattr(exc, "code", "APPLICATION_EXCEPTION"),
                    "message": exc.message,
                }
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "An unexpected internal server error occurred.",
                }
            },
        )


def setup_middlewares(app: FastAPI) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Adjust as necessary for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
