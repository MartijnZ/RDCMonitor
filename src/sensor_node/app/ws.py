# src/sensor_node/app/ws.py
from fastapi import APIRouter, WebSocket
router = APIRouter()

async def _relay(bus, topic: str, websocket: WebSocket):
    q = bus.subscribe(topic)
    while True:
        await websocket.send_json({"topic": topic, "payload": await q.get()})

@router.websocket("/ws")
async def ws(websocket: WebSocket):
    await websocket.accept()
    bus = websocket.app.state.bus
    # Speed-only MVP: one relay
    await _relay(bus, "speed", websocket)
