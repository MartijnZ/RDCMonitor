# api.py
from fastapi import APIRouter, Depends
from ..services.state import State
from ..models import SpeedSample  # optional: for response_model typing


router = APIRouter()

@router.get("/health")
def health(): return {"ok": True}

@router.get("/latest", response_model=dict)
def latest(state: State = Depends(State.dep)):
    return {"speed": state.latest_speed} #, "frf": state.latest_frf}

# ws.py
from fastapi import APIRouter, WebSocket
router = APIRouter()

async def _relay(bus, topic, websocket: WebSocket):
    q = bus.subscribe(topic)
    while True: await websocket.send_json(await q.get())

@router.websocket("/ws")
async def ws(websocket: WebSocket):
    await websocket.accept()
    # multiplex both topics
    await _relay  # placeholder, in practice spawn two tasks and gather
