import json
import logging

from fastapi import WebSocket

logger = logging.getLogger("samadhan.ws")


class ConnectionManager:
    def __init__(self) -> None:
        self._connections: dict[str, list[WebSocket]] = {}

    async def connect(self, user_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self._connections.setdefault(user_id, []).append(websocket)

    def disconnect(self, user_id: str, websocket: WebSocket) -> None:
        conns = self._connections.get(user_id, [])
        if websocket in conns:
            conns.remove(websocket)
        if not conns and user_id in self._connections:
            del self._connections[user_id]

    async def send_to_user(self, user_id: str, payload: dict) -> None:
        for ws in list(self._connections.get(user_id, [])):
            try:
                await ws.send_text(json.dumps(payload))
            except Exception:
                logger.warning("Failed to push WS message to user %s; dropping connection.", user_id)
                self.disconnect(user_id, ws)


manager = ConnectionManager()
