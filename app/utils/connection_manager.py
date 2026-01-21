import time

from fastapi import WebSocket

from app.schemas.websocket import ActiveConnection, WebSocketOutput


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, ActiveConnection] = {}

    async def connect(self, session_id: str, websocket: WebSocket):
        await websocket.accept()
        connection = {"websocket": websocket, "last_seen": time.time()}
        self.active_connections[session_id] = ActiveConnection.model_validate(
            connection
        )
        await self.send_json(
            session_id, {"type": "connection_status", "status": "connected"}
        )

    async def disconnect(self, session_id: str):
        websocket = self.active_connections[session_id].websocket
        await self.send_json(
            session_id, {"type": "connection_status", "status": "disconnected"}
        )
        await websocket.close()
        del self.active_connections[session_id]

    async def send_json(self, session_id: str, payload: dict):
        websocket = self.active_connections[session_id].websocket
        data = WebSocketOutput.model_validate({"payload": payload})
        await websocket.send_json(data.model_dump())

    def update_activity(self, session_id: str):
        self.active_connections[session_id].last_seen = time.time()

    async def check_stale(self, max_inactivity: int = 300):
        current_time = time.time()
        to_close = []
        for session_id, connection in self.active_connections.items():
            if current_time - connection.last_seen > max_inactivity:
                to_close.append(session_id)

        for session_id in to_close:
            await self.disconnect(session_id)

    # TODO: detect and close stale connections
    # TODO: handle send fails
    # TODO: KeyError
    # TODO: cleaning and proper testing


connection_manager = ConnectionManager()
