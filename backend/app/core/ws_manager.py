import asyncio
import json
import logging

from fastapi import WebSocket

logger = logging.getLogger("app")


class ConnectionManager:
    """In-memory registry of live WebSocket clients for this process.

    One instance per server process -- fine for a single-instance
    deployment. Behind multiple app workers, each worker only
    broadcasts to its own connected clients (the pg LISTEN below runs
    per-process, so every worker still hears every NOTIFY and forwards
    it to whichever clients happen to be attached to it).
    """

    def __init__(self):
        self._connections: set[WebSocket] = set()
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        async with self._lock:
            self._connections.add(websocket)

    async def disconnect(self, websocket: WebSocket) -> None:
        async with self._lock:
            self._connections.discard(websocket)

    async def broadcast(self, message: dict) -> None:
        payload = json.dumps(message)
        async with self._lock:
            targets = list(self._connections)
        for ws in targets:
            try:
                await ws.send_text(payload)
            except Exception:
                logger.warning(
                    "Dropping unresponsive websocket client", exc_info=True
                )
                await self.disconnect(ws)


analytics_ws_manager = ConnectionManager()
