from pydantic import BaseModel
from typing import List

class SpeedSample(BaseModel):
    t_ns: int
    speed_mps: float

class FRFResult(BaseModel):
    t_ns: int
    f_hz: List[float]
    H1_real: List[float]
    H1_imag: List[float]
    coh: List[float]  # coherence

class QRConfig(BaseModel):
    # minimal example; extend as needed
    hat_sample_rate: int | None = None
    frf_navg: int | None = None
    push_url: str | None = None
