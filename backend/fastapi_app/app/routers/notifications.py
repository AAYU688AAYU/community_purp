from fastapi import APIRouter, HTTPException, Depends, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from ..utils.auth import get_current_user

router = APIRouter()

# In-memory storage for connected clients (in production, use Redis)
connected_users = {}

class Notification(BaseModel):
    id: str
    user_id: str
    title: str
    message: str
    type: str
    read: bool = False
    created_at: datetime = datetime.utcnow()
    data: Optional[dict] = None

@router.websocket("/ws")
async def notifications_websocket(websocket: WebSocket):
    await websocket.accept()
    
    try:
        # Get user info from token
        token = websocket.headers.get("authorization", "").replace("Bearer ", "")
        user = await get_current_user(token)
        user_id = user["sub"]
        
        # Store the connection
        if user_id not in connected_users:
            connected_users[user_id] = []
        connected_users[user_id].append(websocket)
        
        try:
            while True:
                # Keep the connection alive
                await websocket.receive_text()
        except WebSocketDisconnect:
            connected_users[user_id].remove(websocket)
            if not connected_users[user_id]:
                del connected_users[user_id]
                
    except Exception as e:
        await websocket.close(code=1001, reason=str(e))

async def send_notification(user_id: str, notification: Notification):
    """Send notification to a specific user"""
    if user_id in connected_users:
        for websocket in connected_users[user_id]:
            try:
                await websocket.send_json(notification.dict())
            except:
                # Remove dead connections
                connected_users[user_id].remove(websocket)
        
        if not connected_users[user_id]:
            del connected_users[user_id]

async def broadcast_notification(notification: Notification, exclude_user_id: Optional[str] = None):
    """Broadcast notification to all connected users except excluded one"""
    for user_id, websockets in connected_users.items():
        if user_id != exclude_user_id:
            for websocket in websockets:
                try:
                    await websocket.send_json(notification.dict())
                except:
                    websockets.remove(websocket)
            
            if not websockets:
                del connected_users[user_id]

@router.post("/send/{user_id}")
async def send_user_notification(
    user_id: str,
    notification: Notification,
    current_user: dict = Depends(get_current_user)
):
    """Send notification to a specific user"""
    try:
        await send_notification(user_id, notification)
        return {"status": "notification_sent"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/broadcast")
async def broadcast_to_all(
    notification: Notification,
    current_user: dict = Depends(get_current_user)
):
    """Broadcast notification to all users"""
    try:
        await broadcast_notification(notification)
        return {"status": "notification_broadcast"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 