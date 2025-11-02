from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    ws_path: str = "/ws"
    push_url: str = "https://example.com/ingest"
    push_period_s: float = 5.0
    speed_gpio_a: int = 23      # adjust to your wiring
    speed_gpio_b: int | None = None  # set if quadrature
    hat_sample_rate: int = 2048
    hat_block_size: int = 1024
    frf_navg: int = 8
    frf_window: str = "hann"
    qr_device: str | None = None    # e.g., "/dev/input/event2" or serial tty
    offline_db: str = "/var/lib/rpi-sensor-node/queue.db"
    model: str = "rpi-4b"  # informational

    class Config:
        env_file = ".env"
