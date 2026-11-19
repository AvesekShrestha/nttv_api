import asyncio
import json
import logging
from typing import Literal

from fastapi import (
    APIRouter,
    HTTPException,
    WebSocket,
    WebSocketDisconnect,
)
from pydantic import BaseModel, ConfigDict, Field

from src.api.authentication import authenticate_access_token
from src.infrastructure.realtime.connection_manager import (
    ConnectionManager,
)


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"],
)

AUTH_RECHECK_SECONDS = 30


class SocketAuthentication(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: Literal["authenticate"]
    access_token: str = Field(
        min_length=1,
        max_length=8192,
    )


async def close_socket(
    websocket: WebSocket,
    code: int,
) -> None:
    try:
        await websocket.close(code=code)

    except (
        WebSocketDisconnect,
        RuntimeError,
        OSError,
    ):
        pass


async def recheck_authentication(
    websocket: WebSocket,
    token: str,
    user_id: str,
) -> None:
    while True:
        await asyncio.sleep(AUTH_RECHECK_SECONDS)

        try:
            user = await authenticate_access_token(
                token,
                websocket.app.state.authentication_http_client,
            )

            if user.id != user_id:
                await close_socket(websocket, 1008)
                return

        except HTTPException as exc:
            await close_socket(
                websocket,
                1013 if exc.status_code == 503 else 1008,
            )
            return

        except Exception as exc:
            logger.error(
                "WebSocket auth recheck failed: %s",
                type(exc).__name__,
            )
            await close_socket(websocket, 1011)
            return


@router.websocket("/ws")
async def notification_websocket(websocket: WebSocket):
    manager: ConnectionManager = (
        websocket.app.state.connection_manager
    )
    recheck_task: asyncio.Task | None = None

    await websocket.accept()

    try:
        raw = await asyncio.wait_for(
            websocket.receive_text(),
            timeout=10.0,
        )

        if len(raw) > 16384:
            await close_socket(websocket, 1008)
            return

        message = SocketAuthentication.model_validate_json(raw)

        user = await authenticate_access_token(
            message.access_token,
            websocket.app.state.authentication_http_client,
        )

        manager.connect(user.id, websocket)

        sent = await manager.send(
            websocket,
            {
                "type": "ready",
                "user_id": user.id,
            },
        )

        if not sent:
            return

        recheck_task = asyncio.create_task(
            recheck_authentication(
                websocket,
                message.access_token,
                user.id,
            )
        )

        while True:
            raw = await websocket.receive_text()

            if (
                len(raw) > 16384
                or json.loads(raw) != {"type": "ping"}
            ):
                await close_socket(websocket, 1008)
                return

            if not await manager.send(
                websocket,
                {"type": "pong"},
            ):
                return

    except WebSocketDisconnect:
        pass

    except HTTPException as exc:
        await close_socket(
            websocket,
            1013 if exc.status_code == 503 else 1008,
        )

    except (ValueError, KeyError, TimeoutError):
        await close_socket(websocket, 1008)

    finally:
        manager.disconnect(websocket)

        if recheck_task is not None:
            recheck_task.cancel()
            await asyncio.gather(
                recheck_task,
                return_exceptions=True,
            )
