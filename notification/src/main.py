from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

import httpx
from fastapi import FastAPI

from src.api.routes.notifications import (
    router as notifications_router,
)
from src.api.routes.notification_websocket import (
    router as websocket_router,
)
from src.config.settings import settings
from src.infrastructure.persistence.sqlalchemy.database import (
    engine,
)
from src.infrastructure.realtime.connection_manager import (
    ConnectionManager,
)
from src.infrastructure.realtime.postgres_inbox_listener import (
    PostgresInboxListener,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    manager = ConnectionManager()
    app.state.connection_manager = manager

    listener = PostgresInboxListener(
        database_url=settings.database_url,
        manager=manager,
    )

    async with httpx.AsyncClient(
        base_url=settings.authentication_service_url,
        timeout=settings.authentication_api_timeout_seconds,
        follow_redirects=False,
    ) as client:
        app.state.authentication_http_client = client

        try:
            await listener.start()
            yield

        finally:
            try:
                await listener.stop()

            finally:
                await engine.dispose()


app = FastAPI(
    title="NTC Notification Service",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "PATCH"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(
    notifications_router,
    prefix="/api/v1",
)

app.include_router(
    websocket_router,
    prefix="/api/v1",
)


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "notification-service",
    }
