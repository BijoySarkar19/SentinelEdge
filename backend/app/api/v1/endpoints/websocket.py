from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.websocket.manager import manager
from app.monitoring.metrics import ACTIVE_WEBSOCKET_CONNECTIONS

router = APIRouter()

@router.websocket("/events")
async def websocket_events_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    ACTIVE_WEBSOCKET_CONNECTIONS.inc()
    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        ACTIVE_WEBSOCKET_CONNECTIONS.dec()
