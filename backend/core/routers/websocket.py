from typing import Dict, List, Set
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from ..logging_config import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/ws", tags=["Real-time Operations"])

class ConnectionManager:
    """Manages active WebSocket connections for real-time alerting."""
    
    def __init__(self):
        # Maps user_id to a set of active websocket connections
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)
        logger.info(f"WebSocket: User {user_id} connected. Pool size: {len(self.active_connections[user_id])}")

    def disconnect(self, websocket: WebSocket, user_id: str):
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        logger.info(f"WebSocket: User {user_id} disconnected.")

    async def broadcast(self, message: dict):
        """Sends a message to all active admin connections."""
        # For now, we broadcast to all connected users who are likely admins 
        # (Filtering should be done based on role in a production environment)
        for user_id, connections in self.active_connections.items():
            for connection in connections:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"WebSocket: Failed to send to {user_id}: {e}")

    async def send_to_user(self, user_id: str, message: dict):
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"WebSocket: Individual send failed: {e}")

manager = ConnectionManager()

@router.websocket("/events/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await manager.connect(websocket, user_id)
    try:
        while True:
            # Keep the connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
    except Exception as e:
        logger.error(f"WebSocket Error: {e}")
        manager.disconnect(websocket, user_id)

# Store connected clients
connected_clients = []

@router.websocket("/ws/approvals")
async def approvals_websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    try:
        while True:
            # Keep the connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        connected_clients.remove(websocket)

# Function to broadcast messages to all connected clients
async def broadcast_approval_update(message: str):
    for client in connected_clients:
        await client.send_text(message)
