from fastapi import FastAPI

from src.api.rest_api.auth_controller import router

app = FastAPI()

app.include_router(router, prefix="/api", )

