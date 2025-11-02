import asyncio, json
from evdev import InputDevice, categorize, ecodes

class QRScanner:

    def __init__(self, path:str):
        self.path = path
        self._dev = None

    async def start(self):
        self._dev = InputDevice(self.path)
        self._dev.grab()

    async def read_json(self):
        buf = ""

        async for ev in self._dev.async_read_loop():
            if ev.type != ecodes.EV_KEY: continue
            e = categorize(ev)

            if e.keystate != e.key_up: continue
            key = e.keycode.replace("KEY_", "")

            if key == "ENTER":
                return json.loads(buf)  # QR encodes JSON config
            elif len(key) == 1:
                buf += key.lower()
