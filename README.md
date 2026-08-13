# Yarn Length Tracker

A real-time yarn length measurement tool built with an Arduino Nano, KY-040 rotary encoder, and Python. Designed to work with a handmade umbrella-style yarn swift to track how much yarn has been wound during a session.

## How It Works

A rotary encoder is mounted at the base of the yarn swift via a gear mechanism. As the swift rotates, the encoder counts pulses and the Arduino calculates yarn length based on the swift's diameter and a geometric correction factor. Data is sent over USB serial to a Python interface that displays live length, logs completed balls, generates a real-time chart, and saves session summaries.

## Hardware Required

- Arduino Nano (clone with CH340 chip)
- KY-040 rotary encoder module
- USB Mini-B cable
- Jumper wires
- 3D printed mounting bracket and gears (designed for this specific swift)

## Wiring

| KY-040 Pin | Arduino Nano Pin |
|---|---|
| GND | GND |
| + (VCC) | 5V |
| CLK | D2 |
| DT | D3 |
| SW | D4 |

## Software Requirements

**Arduino:**
- Arduino IDE 2.x
- Board: Arduino Nano
- Processor: ATmega328P (not Old Bootloader — may vary by clone)

**Python:**
```bash
pip install pyserial matplotlib
```

## Setup and Usage

1. Upload `yarn_tracker.ino` to the Arduino Nano using Arduino IDE
2. Disconnect from Arduino IDE (close Serial Monitor)
3. Run `yarn_tracker.py` in Python
4. Enter the swift's tip-to-tip diameter in cm when prompted
5. Wind yarn — length updates in real time in the terminal and on the chart
6. Press **R** in the terminal or the encoder button to log a completed ball and reset
7. Press **Ctrl+C** to end the session and view the summary
8. Optionally save the session log to a timestamped text file

## Configuration

Two constants at the top of the Arduino sketch can be adjusted:

```cpp
const int PULSES_PER_REV = 40;      // encoder pulses per full swift rotation
const float GEOMETRY_FACTOR = 2.75; // yarn path correction factor
```

**PULSES_PER_REV** depends on your specific gear ratio. If your encoder and swift shaft gears are the same size (1:1 ratio), and your KY-040 produces 40 pulses per revolution (20 physical clicks × 2 pulses per click), leave this at 40. Adjust if your gear ratio differs.

**GEOMETRY_FACTOR** corrects for the fact that the yarn path follows the hexagonal arm geometry of the swift rather than a perfect circle. The default value of 2.75 was determined through physical testing on this specific swift design. If you use this with a different swift, calibrate by measuring a known length of yarn and adjusting this value until the tracker matches.

## Known Limitations

**Geometric constant requires calibration** — the default GEOMETRY_FACTOR of 2.75 was tuned through testing on one specific swift design. Different swift geometries, arm counts, or arm lengths will produce different yarn paths and may require recalibration. To calibrate: wind a measured length of yarn (e.g. measure out exactly 5 yards), run the tracker, and compare the reported length to the known length. Adjust GEOMETRY_FACTOR proportionally until they match.

**Speed sensitivity** — the encoder uses hardware interrupts for reliable pulse counting, but very high winding speeds may still produce occasional missed or double-counted pulses due to contact bounce in the mechanical encoder. At normal hand-winding speeds (roughly 1-3 revolutions per second) accuracy is good. Very slow winding (below ~0.5 rev/sec) can also produce inconsistent counts due to contact bounce at low signal transition speeds. For best accuracy wind at a steady moderate pace.

**Gear slip** — if the mounting bracket is loose or the gears are not firmly meshed, pulses can be missed, causing under-reporting. Ensure the bracket is firmly seated and the gears mesh with minimal backlash before each session.

**Serial buffer** — at very high encoder speeds the Arduino may produce serial data faster than Python can consume it. The Python interface includes a buffer flush to handle this, but extended high-speed winding may cause brief display lag.

**Diameter measurement** — enter the tip-to-tip diameter across the widest point of the swift arms. The geometric correction factor accounts for the difference between the circumscribed circle and the actual hexagonal yarn path, so do not pre-correct your measurement.

## Project Context

This project was developed as part of the University of Cincinnati Experiential Education Program (EEP). It serves as the hardware-software integration component of a broader semester project that also included designing and 3D printing the yarn swift itself and building a Python engineering calculator.

## Author

Ethan DeMoss  
University of Cincinnati — Mechanical Engineering  
[linkedin.com/in/Ethan-DeMoss](https://www.linkedin.com/in/Ethan-DeMoss)  
[Engineering Calculator Repository](https://github.com/EthanDeMoss-eng/engineering-calculator)
