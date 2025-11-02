# src/sensor_node/services/state.py
from typing import Optional, Dict, Any
from fastapi import Request

class State:
    """
    Lightweight in-proc cache of the most recent samples.
    Store plain dicts; validate only at I/O boundaries.
    """
    def __init__(self) -> None:
        self.latest_speed: Optional[Dict[str, Any]] = None

    # FastAPI dependency provider
    @staticmethod
    def dep(request: Request) -> "State":
        return request.app.state.state
