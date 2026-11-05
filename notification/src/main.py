from fastapi import FastAPI

from src.api.routes.notifications import router as notifications_router

app = FastAPI(
    title="NTC Notification Service",
    version="1.0.0",
)

app.include_router(notifications_router, prefix="/api/v1")


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "notification-service",
    }
