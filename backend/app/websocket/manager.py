from collections import defaultdict
from typing import Any

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: dict[str, set[WebSocket]] = defaultdict(set)

    async def connect(self, user_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections[user_id].add(websocket)

    def disconnect(self, user_id: str, websocket: WebSocket) -> None:
        connections = self.active_connections.get(user_id)
        if not connections:
            return

        connections.discard(websocket)
        if not connections:
            self.active_connections.pop(user_id, None)

    async def send_to_user(self, user_id: str, payload: dict[str, Any]) -> None:
        connections = list(self.active_connections.get(user_id, set()))

        for websocket in connections:
            try:
                await websocket.send_json(payload)
            except RuntimeError:
                self.disconnect(user_id, websocket)


connection_manager = ConnectionManager()
