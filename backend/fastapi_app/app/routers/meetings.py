from fastapi import APIRouter, HTTPException, Depends, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from ..utils.auth import get_current_user
import json

router = APIRouter()

# In-memory storage for active meetings (in production, use Redis or similar)
active_meetings = {}
connected_clients = {}

class MeetingParticipant(BaseModel):
    user_id: str
    name: str
    role: str
    audio_enabled: bool = True
    video_enabled: bool = True

class MeetingState(BaseModel):
    meeting_id: str
    participants: List[MeetingParticipant]
    is_recording: bool = False
    chat_enabled: bool = True
    screen_sharing_user_id: Optional[str] = None

@router.websocket("/ws/{meeting_id}")
async def websocket_endpoint(websocket: WebSocket, meeting_id: str):
    await websocket.accept()
    
    try:
        # Get user info from token
        token = websocket.headers.get("authorization", "").replace("Bearer ", "")
        user = await get_current_user(token)
        
        if meeting_id not in active_meetings:
            active_meetings[meeting_id] = MeetingState(
                meeting_id=meeting_id,
                participants=[]
            )
        
        # Add participant to meeting
        participant = MeetingParticipant(
            user_id=user["sub"],
            name=user["name"],
            role=user["role"]
        )
        active_meetings[meeting_id].participants.append(participant)
        connected_clients[websocket] = {"meeting_id": meeting_id, "user": user}
        
        # Notify others about new participant
        await broadcast_to_meeting(meeting_id, {
            "type": "participant_joined",
            "data": participant.dict()
        }, exclude=websocket)
        
        # Send current meeting state to new participant
        await websocket.send_json({
            "type": "meeting_state",
            "data": active_meetings[meeting_id].dict()
        })
        
        while True:
            message = await websocket.receive_json()
            
            # Handle different message types
            if message["type"] == "audio_toggle":
                participant.audio_enabled = message["enabled"]
            elif message["type"] == "video_toggle":
                participant.video_enabled = message["enabled"]
            elif message["type"] == "screen_share_start":
                active_meetings[meeting_id].screen_sharing_user_id = user["sub"]
            elif message["type"] == "screen_share_stop":
                active_meetings[meeting_id].screen_sharing_user_id = None
            elif message["type"] == "chat_message":
                # Add timestamp and sender info
                message["data"]["timestamp"] = datetime.utcnow().isoformat()
                message["data"]["sender"] = {
                    "id": user["sub"],
                    "name": user["name"]
                }
            
            # Broadcast message to all participants
            await broadcast_to_meeting(meeting_id, message, include_self=False, exclude=websocket)
            
    except WebSocketDisconnect:
        # Remove participant from meeting
        if websocket in connected_clients:
            meeting_id = connected_clients[websocket]["meeting_id"]
            user = connected_clients[websocket]["user"]
            
            if meeting_id in active_meetings:
                active_meetings[meeting_id].participants = [
                    p for p in active_meetings[meeting_id].participants 
                    if p.user_id != user["sub"]
                ]
                
                # Remove meeting if empty
                if not active_meetings[meeting_id].participants:
                    del active_meetings[meeting_id]
                else:
                    # Notify others about participant leaving
                    await broadcast_to_meeting(meeting_id, {
                        "type": "participant_left",
                        "data": {"user_id": user["sub"]}
                    })
            
            del connected_clients[websocket]
    
    except Exception as e:
        await websocket.close(code=1001, reason=str(e))

async def broadcast_to_meeting(meeting_id: str, message: dict, include_self: bool = True, exclude: WebSocket = None):
    """Broadcast message to all participants in a meeting"""
    for client, data in connected_clients.items():
        if data["meeting_id"] == meeting_id:
            if client != exclude or include_self:
                try:
                    await client.send_json(message)
                except:
                    pass  # Handle disconnected clients

@router.get("/active")
async def get_active_meetings(current_user: dict = Depends(get_current_user)):
    """Get list of active meetings"""
    return {
        meeting_id: state.dict()
        for meeting_id, state in active_meetings.items()
    }

@router.post("/{meeting_id}/recording/start")
async def start_recording(meeting_id: str, current_user: dict = Depends(get_current_user)):
    """Start recording a meeting"""
    if meeting_id not in active_meetings:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    active_meetings[meeting_id].is_recording = True
    await broadcast_to_meeting(meeting_id, {
        "type": "recording_started",
        "data": {"started_by": current_user["sub"]}
    })
    return {"status": "recording_started"}

@router.post("/{meeting_id}/recording/stop")
async def stop_recording(meeting_id: str, current_user: dict = Depends(get_current_user)):
    """Stop recording a meeting"""
    if meeting_id not in active_meetings:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    active_meetings[meeting_id].is_recording = False
    await broadcast_to_meeting(meeting_id, {
        "type": "recording_stopped",
        "data": {"stopped_by": current_user["sub"]}
    })
    return {"status": "recording_stopped"} 