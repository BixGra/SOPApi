from fastapi import WebSocket

from app.schemas.websocket import WebSocketOutput


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, session_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[session_id] = websocket
        await self.send_json(
            session_id, {"type": "connection_status", "status": "connected"}
        )

    async def disconnect(self, session_id: str):
        websocket = self.active_connections[session_id]
        await self.send_json(
            session_id, {"type": "connection_status", "status": "disconnected"}
        )
        await websocket.close()
        del self.active_connections[session_id]

    async def send_json(self, session_id: str, payload: dict):
        websocket = self.active_connections[session_id]
        data = WebSocketOutput.model_validate({"payload": payload})
        await websocket.send_json(data.model_dump())


connection_manager = ConnectionManager()
