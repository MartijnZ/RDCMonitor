import asyncio, aiosqlite, aiohttp, json, time

class Uploader:
    def __init__(self, db_path:str, push_url:str, bus):
        self.db_path=db_path; self.url=push_url; self.bus=bus
    async def start(self):
        self._task = asyncio.create_task(self._run())
        # subscribe to topics to enqueue
        self.bus.subscribe("speed")
        self.bus.subscribe("frf")
    async def _run(self):
        async with aiosqlite.connect(self.db_path) as db, aiohttp.ClientSession(json_serialize=None) as sess:
            await db.execute("CREATE TABLE IF NOT EXISTS q(ts INTEGER, topic TEXT, payload TEXT)")
            await db.commit()
            # consumer loop: flush existing rows then sleep
            while True:
                await self._flush(sess, db)
                await asyncio.sleep(5)
    async def enqueue(self, topic:str, item:dict):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("INSERT INTO q VALUES (?, ?, ?)", (int(time.time()*1e3), topic, json.dumps(item)))
            await db.commit()
    async def _flush(self, sess, db):
        async with db.execute("SELECT rowid, topic, payload FROM q ORDER BY rowid LIMIT 200") as cur:
            rows = await cur.fetchall()
        if not rows: return
        data = [{"topic":t, "payload":json.loads(p)} for _, t, p in rows]
        async with sess.post(self.url, json=data, timeout=10) as r:
            if r.status == 200:
                ids = tuple(r[0] for r in rows)
                await db.execute(f"DELETE FROM q WHERE rowid IN ({','.join('?'*len(ids))})", ids)
                await db.commit()
