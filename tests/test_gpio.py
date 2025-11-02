#!/usr/bin/env python3
"""
Simple GPIO test for a bicycle reed switch speed sensor.
Connect one wire to GPIO 23 (BCM numbering) and the other to GND.

This script:
- Enables an internal pull-up on GPIO 23
- Prints a line each time the magnet passes
- Shows pulse interval and estimated frequency

Run with:  python3 test_reed_sensor.py
Stop with Ctrl+C
"""

import pigpio
import time
import signal
import sys

GPIO_PIN = 23        # BCM numbering
CIRCUMFERENCE_M = 2.1  # meters per wheel revolution (adjust for your wheel)

pi = pigpio.pi()
if not pi.connected:
    print("Error: pigpiod is not running. Start it with: sudo systemctl start pigpiod")
    sys.exit(1)

# configure input with pull-up resistor
pi.set_mode(GPIO_PIN, pigpio.INPUT)
pi.set_pull_up_down(GPIO_PIN, pigpio.PUD_UP)

last_time = None
count = 0

def pulse_callback(gpio, level, tick):
    global last_time, count
    now = time.time()
    if last_time is not None:
        dt = now - last_time
        freq = 1.0 / dt if dt > 0 else 0
        speed_mps = CIRCUMFERENCE_M * freq
        print(f"Pulse {count:5d}: Δt={dt:.3f}s  freq={freq:.2f}Hz  speed={speed_mps:.2f} m/s")
    else:
        print(f"First pulse detected at {now:.3f}s")
    count += 1
    last_time = now

cb = pi.callback(GPIO_PIN, pigpio.FALLING_EDGE, pulse_callback)

print(f"Monitoring GPIO {GPIO_PIN} for reed switch closures…")
print("Move the magnet past the sensor to generate pulses. Press Ctrl+C to exit.")
try:
    signal.pause()  # wait forever, until Ctrl+C
except KeyboardInterrupt:
    print("\nStopped by user.")
finally:
    cb.cancel()
    pi.stop()
