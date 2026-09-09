from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app import models
from app.database import SessionLocal
from app.security import decode_token
from app.ws_manager import manager

router = APIRouter(tags=["realtime"])


@router.websocket("/ws/notifications")
async def ws_notifications(websocket: WebSocket, token: str = Query(...)):
    payload = decode_token(token)
    if payload is None or payload.get("type") != "access":
        await websocket.close(code=4401)
        return

    db: Session = SessionLocal()
    user = db.get(models.User, payload.get("sub"))
    db.close()
    if user is None:
        await websocket.close(code=4401)
        return

    await manager.connect(user.id, websocket)
    try:
        while True:
            # Client doesn't need to send anything; we just keep the socket
            # open and push server->client. Reading lets us detect disconnect.
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(user.id, websocket)
