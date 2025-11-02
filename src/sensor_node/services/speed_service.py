import asyncio, time
from ..drivers.speedometer import Speedometer

class SpeedService:
    def __init__(self, drv:Speedometer, bus):
        self.drv = drv; self.bus = bus; self.task = None

    async def start(self):
        await self.drv.start()
        self.task = asyncio.create_task(self._run())

    async def _run(self):
        while True:
            t_ns, v = await self.drv.read()
            self.bus.publish_nowait("speed", {"t_ns": t_ns, "speed_mps": v})
