import asyncio, time, numpy as np
from ..drivers.hat_adc import HatADC
from ..processing.frf import frf_h1

class VibService:
    def __init__(self, adc:HatADC, bus, fs:int, block:int, navg:int, window:str):
        self.adc=adc; self.bus=bus; self.fs=fs; self.block=block; self.navg=navg; self.window=window
        self.task=None
    async def start(self):
        await self.adc.start()
        self.task = asyncio.create_task(self._run())
    async def _run(self):
        buf_x=[]; buf_y=[]
        while True:
            x, y = await self.adc.read_block()
            buf_x.append(x); buf_y.append(y)
            if len(buf_x) >= self.navg:
                X = np.concatenate(buf_x)[:self.navg*self.block]
                Y = np.concatenate(buf_y)[:self.navg*self.block]
                f, H1, coh = frf_h1(X, Y, self.fs, nperseg=self.block, window=self.window, noverlap=self.block//2)
                now = time.monotonic_ns()
                self.bus.publish_nowait("frf", {"t_ns":now, "f_hz":f.tolist(), "H1_real":H1.real.tolist(), "H1_imag":H1.imag.tolist(), "coh":coh.tolist()})
                buf_x.clear(); buf_y.clear()
