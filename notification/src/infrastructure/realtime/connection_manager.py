import asyncio
from typing import Any

from fastapi import WebSocket, WebSocketDisconnect


class ConnectionManager:
    def __init__(self):
        self._connections: dict[str, set[WebSocket]] = {}
        self._owners: dict[WebSocket, str] = {}
        self._locks: dict[WebSocket, asyncio.Lock] = {}

    def connect(
        self,
        user_id: str,
        websocket: WebSocket,
    ) -> None:
        self.disconnect(websocket)

        self._connections.setdefault(user_id, set()).add(
            websocket
        )
        self._owners[websocket] = user_id
        self._locks[websocket] = asyncio.Lock()

    def disconnect(self, websocket: WebSocket) -> None:
        user_id = self._owners.pop(websocket, None)
        self._locks.pop(websocket, None)

        if user_id is None:
            return

        connections = self._connections.get(user_id)

        if connections is not None:
            connections.discard(websocket)

            if not connections:
                self._connections.pop(user_id, None)

    async def send(
        self,
        websocket: WebSocket,
        payload: dict[str, Any],
    ) -> bool:
        lock = self._locks.get(websocket)

        if lock is None:
            return False

        try:
            async with lock:
                await asyncio.wait_for(
                    websocket.send_json(payload),
                    timeout=5.0,
                )

            return True

        except (
            WebSocketDisconnect,
            RuntimeError,
            OSError,
            TimeoutError,
        ):
            self.disconnect(websocket)

            try:
                await websocket.close(code=1013)

            except (
                WebSocketDisconnect,
                RuntimeError,
                OSError,
            ):
                pass

            return False

    async def broadcast(
        self,
        user_id: str,
        payload: dict[str, Any],
    ) -> None:
        connections = tuple(
            self._connections.get(user_id, ())
        )

        await asyncio.gather(
            *(
                self.send(websocket, payload)
                for websocket in connections
            )
        )

    async def broadcast_all(
        self,
        payload: dict[str, Any],
    ) -> None:
        user_ids = tuple(self._connections)

        await asyncio.gather(
            *(
                self.broadcast(user_id, payload)
                for user_id in user_ids
            )
        )
