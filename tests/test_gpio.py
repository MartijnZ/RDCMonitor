#!/usr/bin/env python3
from gpiozero import Button
from signal import pause
import time

GPIO_PIN = 23           # BCM numbering
CIRCUMFERENCE_M = 2.1   # set your wheel circumference (m)

btn = Button(GPIO_PIN, pull_up=True, bounce_time=0.01)  # 10 ms debounce

last_t = None
count = 0

def on_pulse():
    global last_t, count
    t = time.monotonic()
    if last_t is not None:
        dt = t - last_t
        if dt > 0:
            freq = 1.0 / dt
            speed = CIRCUMFERENCE_M * freq
            print(f"Pulse {count:5d}: Δt={dt:.3f}s  freq={freq:.2f}Hz  speed={speed:.2f} m/s")
    else:
        print(f"First pulse detected at t={t:.3f}s")
    last_t = t
    count += 1

btn.when_pressed = on_pulse   # reed closes → pin goes LOW → event fires

print(f"Listening on GPIO {GPIO_PIN} (pull-up enabled). Move the magnet past the sensor. Ctrl+C to exit.")
try:
    pause()
except KeyboardInterrupt:
    pass
