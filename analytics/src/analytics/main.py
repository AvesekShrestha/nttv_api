from fastapi import FastAPI
from analytics.api.v1.analytics_router import router as analytics_router
from analytics.api.middlewares import setup_exception_handlers, setup_middlewares


def create_app() -> FastAPI:
    app = FastAPI(title="Analytics Service API", version="1.0.0")

    setup_middlewares(app)
    setup_exception_handlers(app)

    app.include_router(analytics_router, prefix="/api/v1")

    return app


app = create_app()
