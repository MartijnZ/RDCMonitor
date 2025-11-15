import math
from typing import Optional


class RpmLowPassFilter:
    """
    First-order low-pass filter for RPM.
    dt-aware exponential smoothing:

        alpha = 1 - exp(-dt / tau)
        y = y + alpha * (x - y)

    t is in nanoseconds (monotonic_ns).
    """

    def __init__(self, tau_s: float):
        self.tau_s = tau_s
        self._y: Optional[float] = None
        self._last_t_ns: Optional[int] = None

    def reset(self) -> None:
        self._y = None
        self._last_t_ns = None

    def update(self, x: float, t_ns: int) -> float:
        """
        x: new RPM sample
        t_ns: timestamp from time.monotonic_ns()
        returns filtered RPM
        """
        if self._y is None:
            self._y = x
            self._last_t_ns = t_ns
            return self._y

        dt = (t_ns - self._last_t_ns) / 1e9  # seconds
        self._last_t_ns = t_ns

        if dt <= 0:
            return self._y

        alpha = 1.0 - math.exp(-dt / self.tau_s)
        self._y = self._y + alpha * (x - self._y)
        return self._y
