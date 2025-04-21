# websocket_manager.py
from fastapi import WebSocket
from typing import Dict

class ConnectionManager:
    def __init__(self):
        # Словарь для хранения активных соединений (user_id -> WebSocket)
        self.active_connections: Dict[int, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        print(f"User {user_id} connected")

    def disconnect(self, user_id: int):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
            print(f"User {user_id} disconnected")

    async def send_notification(self, user_id: int, message: str):
        if user_id in self.active_connections:
            websocket = self.active_connections[user_id]
            try:
                await websocket.send_text(message)
                print(f"Notification sent to user {user_id}: {message}")
            except Exception as e:
                print(f"Failed to send notification to user {user_id}: {e}")
                self.disconnect(user_id)
        else:
            print(f"User {user_id} is not connected")

manager = ConnectionManager()