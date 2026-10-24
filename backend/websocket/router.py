
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from backend.websocket.manager import manager


router = APIRouter(tags=["WebSocket"])


@router.websocket("/ws/votes")
async def vote_updates(websocket: WebSocket):
    await manager.connect(websocket)

    try:
        await websocket.send_json({
            "type": "connection",
            "message": "Connected to VoteStream Sentinel live updates",
        })

        while True:
            # Keep the connection alive while the client is connected.
            await websocket.receive_text()

    except WebSocketDisconnect:
        manager.disconnect(websocket)
