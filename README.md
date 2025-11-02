

## Project Layout:

```
rpi-sensor-node/
├─ pyproject.toml
├─ README.md
├─ .env.example
├─ .pre-commit-config.yaml
├─ scripts/
│  ├─ install_deps.sh
│  ├─ dev_run.sh
│  └─ systemd_install.sh
├─ deploy/
│  ├─ rpi-sensor-node.service         # systemd unit
│  └─ udev/99-rpi-sensors.rules       # optional stable device names
├─ src/
│  └─ sensor_node/
│     ├─ __init__.py
│     ├─ main.py                      # entrypoint (starts FastAPI + tasks)
│     ├─ config.py                    # Pydantic settings
│     ├─ logging.py                   # structlog setup
│     ├─ models.py                    # Pydantic schemas
│     ├─ app/
│     │  ├─ api.py                    # REST endpoints
│     │  ├─ ws.py                     # WebSocket endpoints
│     │  └─ metrics.py                # /metrics exporter
│     ├─ drivers/
│     │  ├─ __init__.py
│     │  ├─ speedometer.py            # GPIO/pigpio driver
│     │  ├─ qr_scanner.py             # evdev/serial scanner
│     │  └─ hat_adc.py                # HAT ADC abstraction
│     ├─ processing/
│     │  ├─ __init__.py
│     │  ├─ frf.py                    # FRF calc (Welch, H1)
│     │  └─ filters.py                # optional prefilters/windows
│     ├─ services/
│     │  ├─ bus.py                    # simple async pub/sub (in-proc)
│     │  ├─ speed_service.py          # task producing speed
│     │  ├─ vib_service.py            # task producing FRF
│     │  ├─ qr_service.py             # task applying config from QR
│     │  ├─ uploader.py               # periodic push + offline queue
│     │  └─ state.py                  # current state cache
│     ├─ storage/
│     │  ├─ queue.py                  # aiosqlite offline queue
│     │  └─ files.py                  # optional local CSV/Parquet logs
│     └─ utils/
│        ├─ timebase.py               # monotonic, NTP sanity
│        └─ exceptions.py
└─ tests/
   ├─ test_frf.py
   ├─ test_speedometer.py
   ├─ test_qr.py
   └─ test_api.py
```


CHatGPT Prompt for kick off:

```commandline
Certainly.
Here’s a clean, self-contained summary you can paste into a future chat so the next session picks up exactly where you left off:

---

### 📘 Project summary for next phase

**Goal:**
Develop a Raspberry Pi–based sensing device running Python.
Eventually it will handle speed, QR-based config, and FRF (frequency-response-function) measurement; for now, we’re focusing on the **Speed Service MVP**.

---

### ✅ Current MVP scope

* Measure speed via GPIO or quadrature input using a `Speedometer` driver (pigpio or gpiozero).
* Publish readings on an async in-process `Bus`.
* Maintain the latest sample in a shared `State` cache.
* Expose data through a **FastAPI** service:

  * `GET /api/health`
  * `GET /api/latest` → current speed
  * `WebSocket /ws` → live speed stream.

---

### 🧩 Key Python modules (folder: `src/sensor_node/`)

```
sensor_node/
├─ config.py          # Settings (Pydantic-based)
├─ main.py            # FastAPI app + lifespan tasks
├─ models.py          # Pydantic models for REST responses
├─ app/
│  ├─ api.py          # REST endpoints
│  └─ ws.py           # WebSocket broadcast
├─ services/
│  ├─ bus.py          # simple async pub/sub
│  ├─ speed_service.py# reads speed, publishes to bus
│  └─ state.py        # holds latest values, FastAPI dependency
└─ drivers/
   └─ speedometer.py  # hardware driver (GPIO/pigpio)
```

*(Only these are needed for the MVP; FRF, QR, and upload services come later.)*

---

### 🧠 Architecture notes

* **Concurrency:** Each service runs as an `asyncio` task.
* **Data flow:**
  `Speedometer` → `SpeedService` → `Bus` → (`State`, WebSocket clients, etc.)
* **FastAPI lifespan** creates and shares one `Bus` and `State`.
* **`State`** provides the `/api/latest` snapshot.
* **Pydantic** is used *only* for external I/O (API models, settings). Internal loops use plain dicts or tuples for performance.
* **Logging, error handling, and FRF math** to be added later.

---

### 🧭 Next development steps

1. Verify `SpeedService` produces stable readings on real hardware.
2. Add basic logging (`structlog` or stdlib).
3. Expand `State` to handle vibration/FRF later.
4. Introduce `Uploader` and `QRService` in later milestones.
5. Eventually package as a `systemd` service on the Pi.

---

Copy and paste this summary into a new chat when you resume. It provides enough context for the assistant to reconstruct your progress and continue building out the next components.



```