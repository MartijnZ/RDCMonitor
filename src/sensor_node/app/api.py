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

