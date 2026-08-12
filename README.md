# OWON SPE3103 GUI

Windows control software for the OWON SPE3103 bench power supply (single channel, 30 V / 10 A).
Python, PyQt6, PyVISA over the USB serial port.

Set voltage and current, watch the readings, log to CSV, and have the output shut off when a
threshold is crossed.

## Install

Python 3.11 or newer.

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

NI-VISA is not required, the backend is `pyvisa-py`. The SPE3103 usually shows up as a serial
port (`ASRL3::INSTR`), on some firmware as USBTMC.

## Run

```
python main.py
```

Pick the resource, check the baud rate, hit Connect. The output stays off on connect.

Without hardware:

```
python main.py --demo
```

The simulated supply produces slightly noisy readings and has two buttons that force an OVP or
OCP trip, which is enough to exercise the protection logic.

## SCPI commands

No reliable command reference exists for this device, so `scpi_map.py` holds a list of plausible
candidates per function and `discovery.py` tries them on first connect: queries directly, writes
only with the output off and verified by readback, each followed by `SYST:ERR?`.

Whatever worked is stored in `scpi_profile.json` next to `main.py` and reused on the next start.
Delete the file to force another run. Anything that could not be resolved is marked
"not supported" on the matching control instead of failing silently.

All SCPI strings live in `scpi_map.py` and nowhere else.

## Protection

The device's own OVP/OCP is used when discovery finds the commands: threshold, enable, and a trip
status read in the same poll cycle as the measurements.

A software watchdog runs on top of that at all times. It compares every reading against the
thresholds and jumps the command queue with a shutdown when one is exceeded. Trip delay is
configurable from 0 to 2000 ms so inrush peaks do not trigger it.

The delay integrates the time spent above the threshold instead of restarting the clock on every
sample below it; time below pays it back at half the rate. A load that keeps crossing the limit
therefore still trips, a single peak still does not.

Thresholds only take effect on "Apply protection" — the button is highlighted while the fields
differ from what the watchdog is running on. A threshold above the setpoint (or above the device
rating) can never be reached in normal operation and is called out in the log.

Reset is manual only, via the reset button. While a trip is latched the watchdog does not evaluate
anything, so the output stays locked until it is acknowledged: the button is disabled, a queued
`output_on` is dropped, and the driver refuses the command as a second line of defence.

The software stage can only react as fast as the poll interval allows (100–2000 ms). It is a
convenience, not a fuse, and no substitute for real hardware protection.

## Layout

```
main.py                  entry point, --demo switch
owon_spe3103/
  scpi_map.py            SCPI strings, candidate lists, device limits
  driver.py              PyVISA in its own thread, queue, polling, reconnect
  discovery.py           command probing and profile cache
  protection.py          thresholds and software watchdog
  gui.py                 window and controls
  plot.py                live plot
tests/
  test_protection.py     watchdog logic, no Qt and no device needed
```

```
python tests/test_protection.py
```

The GUI never touches PyVISA. Everything goes through a queue into the worker thread, with a
priority slot for shutdown. Plot data sits in bounded deques so long sessions do not eat memory.

## Building an exe

```
pip install pyinstaller
pyinstaller --onefile --windowed --name OWON-SPE3103 --hidden-import pyvisa_py --collect-submodules pyvisa_py main.py
```

Result lands in `dist/`, around 50 MB because Qt ships along. The folder is not tracked. The exe
writes `scpi_profile.json` next to itself, so put it somewhere writable.

## Rough edges

- CV/CC display is inferred from measured versus set current, not reported by the device
- On a dropped connection the driver retries three times, then gives up
- The candidate lists grew on one specific unit, other firmware may reject more of them

## Safety

Setpoints are clamped to 0–30 V / 0–10 A before sending, protection thresholds to 0–33 V / 0–11 A.
On disconnect and on exit the output goes off, control returns to local, then the port closes.

This is a hobby project driving hardware that can destroy real circuits. Use at your own risk.
