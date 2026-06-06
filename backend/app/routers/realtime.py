from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.websocket import connection_manager


router = APIRouter(tags=["Realtime"])


@router.websocket("/ws/{user_id}")
async def websocket_updates(user_id: str, websocket: WebSocket):
    await connection_manager.connect(user_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        connection_manager.disconnect(user_id, websocket)
