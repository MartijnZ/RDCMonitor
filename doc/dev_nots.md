

## Development Environment


## PI

## NGIX Server & Universal Firewall

Install `nginx`
```commandline
sudo apt install -y nginx
```

Setup ufw:
```commandline
sudo apt install -y ufw

# Allow SSH so you don’t lock yourself out
sudo ufw allow 22/tcp

# Allow HTTP and HTTPS for Nginx
sudo ufw allow 'Nginx Full'   # opens 80 and 443

# (Optional) if you use a custom FastAPI port directly
sudo ufw allow 8000/tcp

# Enable the firewall
sudo ufw enable
```

```commandline
sudo ufw status verbose
```

Deploy nginx
```commandline
sudo cp /opt/rdcmonitor/deploy/nginx/rdc-monitor.conf /etc/nginx/sites-available/
sudo ln -s /etc/nginx/sites-available/rdc-monitor.conf /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

Create `rdc-monitor.conf` (also in git under `scripts`)
```commandline
server {
  listen 80;
  listen [::]:80;
  server_name _;

  root /var/www/rdc-monitor;
  index index.html;

  location / {
    try_files $uri $uri/ /index.html;
  }

  # WebSocket → FastAPI on localhost
  location /ws {
    proxy_pass http://127.0.0.1:8000/ws;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_read_timeout 3600;
  }

  # Optional REST proxy
  location /api/ {
    proxy_pass http://127.0.0.1:8000/api/;
  }
}

```

Make symbolic link to sites-enabled:
```commandline
sudo ln -s /etc/nginx/sites-available/rdc-monitor.conf /etc/nginx/sites-enabled/rdc-monitor.conf
sudo rm -f /etc/nginx/sites-enabled/default
```


## Setup Front-end and Backend

### Pull Git repository
```commandline
sudo mkdir -p /opt/rdc-monitor
sudo chown -R martijn:martijn /opt/rdc-monitor
git clone git@github.com:MartijnZ/RDCMonitor.git
```

### Install Python Dependencies
```commandline
cd /opt/rdc-monitor
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt 
```

### Setup back-end service:


Create a file ``

```commandline
[Unit]
Description=RDC Monitor backend (FastAPI)
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=rdc
Group=rdc
WorkingDirectory=/opt/rdc-monitor
EnvironmentFile=/opt/rdc-monitor/.env # This might be an issue
Environment=PYTHONUNBUFFERED=1

# If your entrypoint is a Python module:
ExecStart=/opt/rdc-monitor/.venv/bin/python -m src.sensor_node.main

# If you run uvicorn directly instead, comment the line above and use:
# ExecStart=/opt/rdc-monitor/.venv/bin/uvicorn sensor_node.app.api:app --host 127.0.0.1 --port 8000 --workers 1

Restart=on-failure
RestartSec=3

# Hardening (safe defaults for a web service)
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=full
ProtectHome=true
ReadWritePaths=/opt/rdc-monitor
# If you write logs/data elsewhere, add them to ReadWritePaths

[Install]
WantedBy=multi-user.target
```

### Setup npm and nodejs

```commandline
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs
```

Validate:
```commandline
node -v # expect v20.19.5
npm -v # expect 10.8.2
```

Build:
```commandline
npm i -D @sveltejs/adapter-static    # Install adapter-static
npm ci        # Install dependencies exactly as in packag-lock.json
```

Make the following modifications:
1. Create a file `+layout.ts` in `/src/routes/` with the content:
```commandline
export const prerender = true;
```
2. In svelte.config.js `@sveltejs/adapter-auto` to `@sveltejs/adapter-static`

Then Build:
```
npm run build # compile static UI into build
```
and a `build` folder is created, copy it to the nginx folder:

Create web root:
```commandline
sudo mkdir -p /var/www/rdc-monitor/releases
sudo chown -R martijn:martijn /var/www/rdc-monitor
```


```commandline
ls -lah /var/www/rdc-monitor
# if empty, deploy them:
cd /opt/rdc-monitor/frontend
npm run build
sudo rsync -a --delete build/ /var/www/rdc-monitor/
sudo chown -R www-data:www-data /var/www/rdc-monitor
```

Test nginx & reload
```commandline
sudo nginx -t
sudo systemctl reload nginx
```

### Node LTS 

##### Windows

```
winget install CoreyButler.NVMforWindows
nvm install lts
nvm use lts
node -v
npm -v
```

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


## Where I Left of (2-11-2025)

Here’s a clear, **checkpoint summary** of what you’ve done and what remains to get your Raspberry Pi ready for the reed-switch speed sensor and FastAPI app.

---

## 🧩 System setup checklist

### 1. OS & updates

```bash
sudo apt update && sudo apt full-upgrade -y
```

Use **Raspberry Pi OS Bookworm 64-bit** or later.

---

### 2. Python environment

```bash
cd /opt
sudo mkdir rpi-sensor-node && sudo chown pi:pi rpi-sensor-node
cd rpi-sensor-node
python3 --version       # should show 3.11.x
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
```

---

### 3. Core dependencies

```bash
pip install "uvicorn[standard]" fastapi pydantic pydantic-settings orjson structlog numpy scipy aiosqlite aiohttp
```

*(you can later freeze this to `requirements.txt`)*

---

### 4. GPIO support

Since Raspberry Pi OS Bookworm moved to the **libgpiod / lgpio** interface, skip `pigpio` unless you need DMA timing.

Install:

```bash
sudo apt install -y python3-lgpio python3-gpiozero
sudo adduser $USER gpio
# log out and back in (or reboot)
```

Check:

```bash
ls -l /dev/gpiochip*
groups     # should include 'gpio'
```

Optional (explicit):

```bash
export GPIOZERO_PIN_FACTORY=lgpio
```

---

### 5. Wiring (confirmed correct)

| Sensor lead                                  | Pi connection         | Notes     |
| -------------------------------------------- | --------------------- | --------- |
| 1                                            | GPIO 23 (BCM, pin 16) | Input pin |
| 2                                            | GND (pin 6 or 14)     | Ground    |
| Enable pull-up in software (`pull_up=True`). |                       |           |

---

### 6. Quick test script

Use this (works with `gpiozero + lgpio`):

```python
from gpiozero import Button
from signal import pause
import time

GPIO_PIN = 23
CIRCUMFERENCE_M = 2.1

btn = Button(GPIO_PIN, pull_up=True, bounce_time=0.01)
last = None
count = 0

def on_pulse():
    global last, count
    t = time.monotonic()
    if last:
        dt = t - last
        freq = 1/dt
        speed = CIRCUMFERENCE_M * freq
        print(f"Pulse {count:4d}: {freq:6.2f} Hz  {speed:6.2f} m/s")
    else:
        print("First pulse detected")
    last = t
    count += 1

btn.when_pressed = on_pulse
print("Listening on GPIO 23… Ctrl+C to stop")
pause()
```

Run:

```bash
python3 test_reed_gpiozero.py
```

Expected: every magnet pass prints a pulse line.

---

### 7. FastAPI application (for later)

Once GPIO works, run your service:

```bash
source .venv/bin/activate
python run_server.py   # or ./run_server.sh
```

Access from another machine:

```
http://<pi-ip>:8000/api/health
ws://<pi-ip>:8000/ws
```

---

### 8. (Optional) systemd service

`/etc/systemd/system/rpi-sensor-node.service`

```ini
[Unit]
Description=RPi Sensor Node
After=network-online.target

[Service]
User=pi
WorkingDirectory=/opt/rpi-sensor-node
ExecStart=/opt/rpi-sensor-node/.venv/bin/python run_server.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Enable:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now rpi-sensor-node
```

---

### 9. Current status

✅  OS and Python env ready
✅  Dependencies installed
✅  Wiring correct
🚧  GPIO library fallback fixed by installing `python3-lgpio` and using system Python 3.11
🚧  Next step: confirm pulses appear with the test script before returning to FastAPI integration.

---

When you come back:

1. Verify the test script prints pulses.
2. If it does, we’ll switch the `Speedometer` driver to use `gpiozero` instead of `pigpio`.
3. Then you can re-enable your FastAPI service with real data streaming.
