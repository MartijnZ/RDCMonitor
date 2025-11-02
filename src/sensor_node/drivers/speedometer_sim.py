import asyncio, time, math, random

class SpeedometerSim:
    """
    Generates a pseudo speed (m/s): baseline + slow sine + jitter.
    Emits at ~50 Hz.
    """
    def __init__(self, baseline=5.0, amp=2.0, period_s=8.0, jitter=0.2, hz=50):
        self.baseline = baseline
        self.amp = amp
        self.period = period_s
        self.jitter = jitter
        self.dt = 1.0 / hz
        self._queue = asyncio.Queue(maxsize=1000)
        self._t0 = time.monotonic()

    async def start(self):
        asyncio.create_task(self._run())

    async def _run(self):
        while True:
            t = time.monotonic() - self._t0
            v = self.baseline + self.amp * math.sin(2*math.pi*t/self.period) + random.uniform(-self.jitter, self.jitter)
            ts = time.monotonic_ns()
            try: self._queue.put_nowait((ts, max(0.0, v)))
            except asyncio.QueueFull: pass
            await asyncio.sleep(self.dt)

    async def read(self):
        return await self._queue.get()

    async def stop(self):  # for interface parity
        pass
