import asyncio

class Bus:
    def __init__(self):
        self._subs = {}

    def subscribe(self, topic:str):
        q = asyncio.Queue(10); self._subs.setdefault(topic, []).append(q); return q

    def publish_nowait(self, topic:str, item):
        for q in self._subs.get(topic, []):
            try: q.put_nowait(item)
            except asyncio.QueueFull: pass
