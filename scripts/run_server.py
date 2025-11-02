#!/usr/bin/env python3
"""
Launcher for the RPi Sensor Node FastAPI service.

Usage:
    python run_server.py [--host 0.0.0.0] [--port 8000]
"""

import argparse
import uvicorn
from sensor_node.main import create_app
from sensor_node.config import Settings


def main():
    parser = argparse.ArgumentParser(description="Run the RPi Sensor Node API server")
    parser.add_argument("--host", default=None, help="Host to bind (default from .env or 0.0.0.0)")
    parser.add_argument("--port", type=int, default=None, help="Port to bind (default from .env or 8000)")
    args = parser.parse_args()

    # Load settings from .env (falls back to defaults)
    settings = Settings()

    host = args.host or settings.api_host or "0.0.0.0"
    port = args.port or settings.api_port or 8000

    print(f"Starting FastAPI server on {host}:{port} ...")

    # Launch the FastAPI app defined in sensor_node/main.py
    uvicorn.run(
        "sensor_node.main:create_app",   # use the factory function
        factory=True,
        host=host,
        port=port,
        log_level="info"
    )


if __name__ == "__main__":
    main()
