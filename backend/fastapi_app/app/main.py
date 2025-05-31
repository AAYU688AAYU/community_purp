from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import socketio
from .routers import qr, meetings, notifications

# Create FastAPI app
app = FastAPI(title="CommunityConnect Real-time API",
             description="Real-time features for CommunityConnect",
             version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create Socket.IO server
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins=["http://localhost:3000"])
socket_app = socketio.ASGIApp(sio)

# Include Socket.IO
app.mount("/ws", socket_app)

# Include routers
app.include_router(qr.router, prefix="/api/qr", tags=["QR Codes"])
app.include_router(meetings.router, prefix="/api/meetings", tags=["Virtual Meetings"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["Notifications"])

# Socket.IO event handlers
@sio.event
async def connect(sid, environ):
    print(f"Client connected: {sid}")

@sio.event
async def disconnect(sid):
    print(f"Client disconnected: {sid}")

@sio.event
async def join_meeting(sid, data):
    meeting_id = data.get('meeting_id')
    if meeting_id:
        sio.enter_room(sid, f"meeting_{meeting_id}")
        await sio.emit('user_joined', {'sid': sid}, room=f"meeting_{meeting_id}")

@sio.event
async def leave_meeting(sid, data):
    meeting_id = data.get('meeting_id')
    if meeting_id:
        sio.leave_room(sid, f"meeting_{meeting_id}")
        await sio.emit('user_left', {'sid': sid}, room=f"meeting_{meeting_id}")

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}
