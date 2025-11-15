import asyncio, uvicorn
import contextlib
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI



from .config import Settings
from .services.bus import Bus
from .drivers.speedometer import Speedometer
from .drivers.speedometer_sim import SpeedometerSim
#from .drivers.qr_scanner import QRScanner
#from .drivers.hat_adc import HatADC
from .services.speed_service import SpeedService
#from .services.vib_service import VibService
from .services.uploader import Uploader
from .services.state import State
from .app import api, ws


# ---- logging setup -------------------------------------------------

LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s - %(message)s"

def setup_logging() -> None:
    """
    Configure global logging for the backend.
    Call this exactly once at startup.
    """
    logging.basicConfig(
        level=logging.INFO,        # default level for everything
        format=LOG_FORMAT,
    )

    # Make Speedometer extra chatty when you need it
    # Adjust this string to match the logger name you used in speedometer.py
    # If in speedometer.py you did: logger = logging.getLogger(__name__)
    # and your package is "myapp", full name will be "myapp.drivers.speedometer"
    logging.getLogger("myapp.drivers.speedometer").setLevel(logging.INFO)

    # Optional: keep uvicorn access logs at INFO but reduce its internal noise
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)


# -------------------------------------------------------------------------

async def _state_updater(speed_q, state: State):
    while True:
        item = await speed_q.get()             # {'t_ns': ..., 'speed_mps': ...}
        state.latest_speed = item


def _make_speed_driver(settings: Settings):
    if settings.simulate_speed:
        return SpeedometerSim()
    # real hardware (Pi only)
    return Speedometer(settings.speed_gpio_a, settings.speed_gpio_b)


def create_app() -> FastAPI:
    settings = Settings()
    bus = Bus()
    state = State()

    speed_drv = _make_speed_driver(settings)
    speed_srv = SpeedService(speed_drv, bus)
    speed_q = bus.subscribe("speed")

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # expose shared objects to routes/websocket deps
        app.state.bus = bus
        app.state.state = state

        tasks = [
            asyncio.create_task(speed_srv.start()),
            asyncio.create_task(_state_updater(speed_q, state)),
        ]
        try:
            yield
        finally:
            for t in tasks:
                t.cancel()
                with contextlib.suppress(asyncio.CancelledError):  # noqa
                    await t

    app = FastAPI(title="RPi Sensor Node", lifespan=lifespan)
    app.include_router(api.router, prefix="/api")
    app.include_router(ws.router)
    return app

if __name__ == "__main__":
    setup_logging()
    settings = Settings()
    uvicorn.run(create_app(), host=settings.api_host, port=settings.api_port)

#async def run():
#    settings = Settings()
#    setup_logging()
#    bus = Bus()
#
#    speed_drv = Speedometer(settings.speed_gpio_a, settings.speed_gpio_b)
#    vib_drv   = HatADC(settings.hat_sample_rate, settings.hat_block_size)
#
#    speed = SpeedService(speed_drv, bus)
#    vib   = VibService(vib_drv, bus, settings.hat_sample_rate, settings.hat_block_size, settings.frf_navg, settings.frf_window)
#    uploader = Uploader(settings.offline_db, settings.push_url, bus)
#
#    await asyncio.gather(speed.start(), vib.start(), uploader.start())
#
#if __name__ == "__main__":
#    # Start API and background tasks together
#    app = create_app(Bus())
#    uvicorn.run(app, host=Settings().api_host, port=Settings().api_port)
