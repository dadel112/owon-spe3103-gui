"""Everything that talks to the power supply.
PyVISA is touched only from the QThread in here, the GUI just pushes jobs into
the queue. The demo transport further down replaces the hardware for testing.
"""

from __future__ import annotations

import math
import queue
import random
import time
from dataclasses import dataclass, field

from PyQt6.QtCore import QThread, pyqtSignal

from . import scpi_map
from .discovery import Discovery, profile_path
from .protection import ProtectionManager

PRIO_EMERGENCY = 0
PRIO_USER = 5
PRIO_POLL = 10

DEFAULT_BAUD = 115200
DEFAULT_TIMEOUT_MS = 2000
DEFAULT_POLL_MS = 250
POLL_MIN_MS = 100
POLL_MAX_MS = 2000
RECONNECT_TRIES = 3


# --------------------------------------------------------------------------
# Transports
# --------------------------------------------------------------------------

class VisaTransport:
    """Thin wrapper around a PyVISA resource."""

    def __init__(self, resource: str, baud: int = DEFAULT_BAUD,
                 timeout_ms: int = DEFAULT_TIMEOUT_MS):
        import pyvisa
        self._rm = pyvisa.ResourceManager("@py")
        self._inst = self._rm.open_resource(resource)
        self._inst.timeout = timeout_ms
        self._inst.read_termination = "\n"
        self._inst.write_termination = "\n"
        if hasattr(self._inst, "baud_rate"):
            self._inst.baud_rate = baud

    def write(self, cmd: str) -> None:
        self._inst.write(cmd)

    def query(self, cmd: str) -> str:
        return self._inst.query(cmd).strip()

    def close(self) -> None:
        try:
            self._inst.close()
        finally:
            try:
                self._rm.close()
            except Exception:
                pass


class DemoTransport:
    """Stand-in power supply for --demo. Deliberately understands only the first
    candidate per function so the GUI actually shows an unsupported control now
    and then. Commands are derived from scpi_map, not typed out here.
    """

    UNSUPPORTED = {"measure_power"}

    def __init__(self):
        self._exact: dict[str, str] = {}
        self._param: list[tuple[str, str]] = []
        for key, cands in scpi_map.COMMANDS.items():
            if key in self.UNSUPPORTED or not cands:
                continue
            head = cands[0]
            if "{" in head:
                self._param.append((head.split("{")[0].strip().upper(), key))
            else:
                self._exact[head.strip().upper()] = key
        self.v_set = 0.0
        self.i_set = 1.0
        self.ovp = 33.0
        self.ocp = 11.0
        self.ovp_en = False
        self.ocp_en = False
        self.output = False
        self.tripped = ""
        self.force_ovp = False
        self.force_ocp = False
        self._err = 0
        self._t0 = time.time()

    # -- Simulation ---------------------------------------------------
    def _measure(self) -> tuple[float, float]:
        if not self.output or self.tripped:
            return 0.0, 0.0
        t = time.time() - self._t0
        # A bit of ripple on the voltage plus a slowly breathing load, which
        # looks more alive in the plot than a straight line.
        v = self.v_set * (1.0 + 0.004 * math.sin(t * 1.7)) + random.uniform(-0.004, 0.004)
        load = 6.0 + 1.5 * math.sin(t * 0.4)
        i = min(self.i_set, max(0.0, v / load)) + random.uniform(-0.002, 0.002)
        if self.force_ovp:
            v = self.ovp + 0.6
        if self.force_ocp:
            i = self.ocp + 0.2
        v = max(0.0, v)
        i = max(0.0, i)
        if self.ovp_en and v > self.ovp:
            self.tripped = "OVP"
            self.output = False
        elif self.ocp_en and i > self.ocp:
            self.tripped = "OCP"
            self.output = False
        return v, i

    # -- Command dispatch ----------------------------------------------
    def _resolve(self, cmd: str) -> tuple[str, float | None]:
        norm = cmd.strip().upper()
        if norm in self._exact:
            return self._exact[norm], None
        head, _, tail = norm.partition(" ")
        for prefix, key in self._param:
            if head == prefix:
                try:
                    return key, float(tail)
                except ValueError:
                    return "", None
        return "", None

    def _handle(self, cmd: str) -> str | None:
        key, arg = self._resolve(cmd)
        if key == "system_error":
            code, self._err = self._err, 0
            return f"{code}, {'No error' if code == 0 else 'Undefined header'}"
        if not key:
            self._err = -113
            return None
        v, i = self._measure()
        if key == "idn":
            return "OWON,SPE3103,DEMO-0000,1.0.0-sim"
        if key == "measure_volt":
            return f"{v:.3f}"
        if key == "measure_curr":
            return f"{i:.3f}"
        if key == "set_volt":
            self.v_set = arg or 0.0
        elif key == "set_curr":
            self.i_set = arg or 0.0
        elif key == "get_volt_set":
            return f"{self.v_set:.3f}"
        elif key == "get_curr_set":
            return f"{self.i_set:.3f}"
        elif key == "output_on":
            if not self.tripped:
                self.output = True
        elif key == "output_off":
            self.output = False
        elif key == "output_state":
            return "1" if self.output else "0"
        elif key == "ovp_set":
            self.ovp = arg or 0.0
        elif key == "ocp_set":
            self.ocp = arg or 0.0
        elif key == "ovp_get":
            return f"{self.ovp:.3f}"
        elif key == "ocp_get":
            return f"{self.ocp:.3f}"
        elif key == "ovp_enable":
            self.ovp_en = True
        elif key == "ovp_disable":
            self.ovp_en = False
        elif key == "ocp_enable":
            self.ocp_en = True
        elif key == "ocp_disable":
            self.ocp_en = False
        elif key == "ovp_tripped":
            return "1" if self.tripped == "OVP" else "0"
        elif key == "ocp_tripped":
            return "1" if self.tripped == "OCP" else "0"
        elif key == "prot_clear":
            self.tripped = ""
            self.force_ovp = False
            self.force_ocp = False
        return None

    def write(self, cmd: str) -> None:
        time.sleep(0.002)
        self._handle(cmd)

    def query(self, cmd: str) -> str:
        time.sleep(0.002)
        resp = self._handle(cmd)
        if resp is None:
            raise TimeoutError("keine Antwort (simuliert)")
        return resp

    def close(self) -> None:
        self.output = False


def list_resources() -> list[str]:
    """Available VISA resources, empty list on any error."""
    try:
        import pyvisa
        rm = pyvisa.ResourceManager("@py")
        res = list(rm.list_resources())
        rm.close()
        return res
    except Exception:
        return []


# --------------------------------------------------------------------------
# Command queue
# --------------------------------------------------------------------------

@dataclass(order=True)
class _Job:
    # seq keeps the order stable within one priority and stops PriorityQueue
    # from falling back to comparing the remaining fields on a tie.
    priority: int
    seq: int
    key: str = field(compare=False, default="")
    kwargs: dict = field(compare=False, default_factory=dict)
    raw: str = field(compare=False, default="")
    raw_query: bool = field(compare=False, default=False)
    action: str = field(compare=False, default="cmd")


class PsuDriver(QThread):
    """The worker: holds the connection, drains the queue, polls readings and
    checks whether a protection threshold was crossed.
    """

    reading_ready = pyqtSignal(float, float, float, float)   # v, i, p, ts
    connection_changed = pyqtSignal(bool)
    protection_tripped = pyqtSignal(str, float)              # typ, wert
    log_message = pyqtSignal(str, str)                       # level, text
    error_occurred = pyqtSignal(str)
    profile_ready = pyqtSignal(dict)                         # discovery-ergebnis
    idn_ready = pyqtSignal(str)
    raw_response = pyqtSignal(str)
    mode_changed = pyqtSignal(str)                           # CV / CC / --
    setpoints_read = pyqtSignal(float, float)                # v_set, i_set

    def __init__(self, demo: bool = False, parent=None):
        super().__init__(parent)
        self.demo = demo
        self.protection = ProtectionManager()
        self.demo_device: DemoTransport | None = None
        self._q: queue.PriorityQueue = queue.PriorityQueue()
        self._seq = 0
        self._running = True
        self._transport = None
        self._profile: dict[str, str | None] = {}
        self._poll_ms = DEFAULT_POLL_MS
        self._next_poll = 0.0
        self._pending: tuple[str, int, int] | None = None   # resource, baud, timeout
        self._connected = False
        self._trip_reported = ""

    # -- API called from the GUI thread ---------------------------------
    def _put(self, prio: int, **kw) -> None:
        self._seq += 1
        self._q.put(_Job(prio, self._seq, **kw))

    def request_connect(self, resource: str, baud: int = DEFAULT_BAUD,
                        timeout_ms: int = DEFAULT_TIMEOUT_MS) -> None:
        self._pending = (resource, baud, timeout_ms)
        self._put(PRIO_USER, action="connect")

    def request_disconnect(self) -> None:
        self._put(PRIO_EMERGENCY, action="disconnect")

    def send(self, key: str, priority: int = PRIO_USER, **kwargs) -> None:
        self._put(priority, key=key, kwargs=kwargs)

    def emergency_off(self) -> None:
        self._put(PRIO_EMERGENCY, key="output_off")

    def send_raw(self, text: str, is_query: bool) -> None:
        self._put(PRIO_USER, action="raw", raw=text, raw_query=is_query)

    def set_poll_interval(self, ms: int) -> None:
        self._poll_ms = max(POLL_MIN_MS, min(POLL_MAX_MS, int(ms)))

    def supports(self, key: str) -> bool:
        """True if discovery resolved this function."""
        return bool(self._profile.get(key))

    def profile(self) -> dict:
        return dict(self._profile)

    def stop(self) -> None:
        self._running = False
        self._put(PRIO_EMERGENCY, action="quit")

    # -- Thread -------------------------------------------------------
    def run(self) -> None:
        # Short queue timeout instead of a blocking get(), otherwise polling
        # would never get a turn while nobody clicks anything.
        while self._running:
            try:
                job = self._q.get(timeout=0.02)
            except queue.Empty:
                job = None
            if job is not None:
                try:
                    self._dispatch(job)
                except Exception as exc:
                    self._fail(exc)
                if job.action == "quit":
                    break
            if self._connected and time.monotonic() >= self._next_poll:
                self._next_poll = time.monotonic() + self._poll_ms / 1000.0
                try:
                    self._poll()
                except Exception as exc:
                    self._fail(exc)
        self._shutdown()

    def _dispatch(self, job: _Job) -> None:
        if job.action == "connect":
            self._open()
        elif job.action in ("disconnect", "quit"):
            self._shutdown()
        elif job.action == "raw":
            self._raw(job.raw, job.raw_query)
        elif job.key:
            self._exec(job.key, **job.kwargs)

    # -- Connection -----------------------------------------------------
    def _open(self) -> None:
        if self._pending is None:
            return
        resource, baud, timeout_ms = self._pending
        self._shutdown(quiet=True)
        try:
            if self.demo:
                self.demo_device = DemoTransport()
                self._transport = self.demo_device
                self.log_message.emit("INFO", "Demo-Geraet gestartet (simuliert)")
            else:
                self._transport = VisaTransport(resource, baud, timeout_ms)
                self.log_message.emit("INFO", f"Verbunden mit {resource} @ {baud} Bd")
        except Exception as exc:
            self._transport = None
            self.error_occurred.emit(f"Verbindung fehlgeschlagen: {exc}")
            self.connection_changed.emit(False)
            return

        disc = Discovery(self._transport, self._log)
        self._profile, idn = disc.run(profile_path(), demo=self.demo)
        self.idn_ready.emit(idn)
        self.profile_ready.emit(dict(self._profile))
        self.protection.set_hardware(
            ovp=self.supports("ovp_set") and self.supports("ovp_enable"),
            ocp=self.supports("ocp_set") and self.supports("ocp_enable"),
            ovp_trip=self.supports("ovp_tripped"),
            ocp_trip=self.supports("ocp_tripped"),
        )
        self._exec("remote")
        self._exec("output_off")          # never switch on by itself
        self._read_setpoints()
        self._connected = True
        self._trip_reported = ""
        self._next_poll = 0.0
        self.connection_changed.emit(True)

    def _shutdown(self, quiet: bool = False) -> None:
        # Order matters: output off first, then hand control back to the front
        # panel, and only then close the port.
        if self._transport is None:
            self._connected = False
            return
        try:
            self._exec("output_off")
            self._exec("local")
        except Exception:
            pass
        try:
            self._transport.close()
        except Exception:
            pass
        self._transport = None
        self.demo_device = None
        self._connected = False
        if not quiet:
            self.log_message.emit("INFO", "Verbindung geschlossen")
            self.connection_changed.emit(False)

    def _fail(self, exc: Exception) -> None:
        self.error_occurred.emit(str(exc))
        self.log_message.emit("ERROR", f"VISA-Fehler: {exc}")
        if not self._connected or self._pending is None:
            return
        self._connected = False
        self.connection_changed.emit(False)
        try:
            if self._transport is not None:
                self._transport.close()
        except Exception:
            pass
        self._transport = None
        for attempt in range(1, RECONNECT_TRIES + 1):
            if not self._running:
                return
            self.log_message.emit("WARN", f"Reconnect-Versuch {attempt}/{RECONNECT_TRIES}")
            QThread.msleep(1000)
            try:
                self._open()
                if self._connected:
                    return
            except Exception as exc2:
                self.log_message.emit("ERROR", f"Reconnect fehlgeschlagen: {exc2}")
        self.error_occurred.emit("Reconnect endgueltig fehlgeschlagen")

    # -- Commands -------------------------------------------------------
    def _log(self, level: str, text: str) -> None:
        self.log_message.emit(level, text)

    def _exec(self, key: str, **kwargs) -> str | None:
        if self._transport is None:
            return None
        template = self._profile.get(key)
        if not template:
            self.log_message.emit("WARN", f"'{key}' vom Geraet nicht unterstuetzt")
            return None
        cmd = scpi_map.render(template, **kwargs) if kwargs else template
        self.log_message.emit("TX", cmd)
        if scpi_map.is_query(key):
            resp = self._transport.query(cmd)
            self.log_message.emit("RX", resp)
            return resp
        self._transport.write(cmd)
        return None

    def _raw(self, text: str, is_query: bool) -> None:
        if self._transport is None or not text.strip():
            return
        self.log_message.emit("TX", text)
        if is_query:
            resp = self._transport.query(text)
            self.log_message.emit("RX", resp)
            self.raw_response.emit(resp)
        else:
            self._transport.write(text)

    def _num(self, key: str, **kwargs) -> float | None:
        resp = self._exec(key, **kwargs)
        if resp is None:
            return None
        try:
            return float(resp.split(",")[0])
        except ValueError:
            return None

    def _read_setpoints(self) -> None:
        v = self._num("get_volt_set")
        i = self._num("get_curr_set")
        if v is not None or i is not None:
            self.setpoints_read.emit(v or 0.0, i or 0.0)

    # -- Setpoints and protection, all clamped --------------------------
    def apply_voltage(self, volt: float) -> None:
        v = max(0.0, min(scpi_map.V_MAX, float(volt)))
        self.send("set_volt", v=v)

    def apply_current(self, amp: float) -> None:
        i = max(0.0, min(scpi_map.I_MAX, float(amp)))
        self.protection.set_setpoint_current(i)
        self.send("set_curr", i=i)

    def apply_ovp(self, volt: float, enabled: bool) -> None:
        v = max(0.0, min(scpi_map.OVP_MAX, float(volt)))
        self.protection.set_ovp(v, enabled)
        if self.supports("ovp_set"):
            self.send("ovp_set", v=v)
        if enabled and self.supports("ovp_enable"):
            self.send("ovp_enable")
        elif not enabled and self.supports("ovp_disable"):
            self.send("ovp_disable")

    def apply_ocp(self, amp: float, enabled: bool) -> None:
        i = max(0.0, min(scpi_map.OCP_MAX, float(amp)))
        self.protection.set_ocp(i, enabled)
        if self.supports("ocp_set"):
            self.send("ocp_set", i=i)
        if enabled and self.supports("ocp_enable"):
            self.send("ocp_enable")
        elif not enabled and self.supports("ocp_disable"):
            self.send("ocp_disable")

    def clear_protection(self) -> None:
        self.protection.reset()
        self._trip_reported = ""
        self.send("prot_clear", priority=PRIO_EMERGENCY)

    # -- Polling ------------------------------------------------------
    def _poll(self) -> None:
        v = self._num("measure_volt")
        i = self._num("measure_curr")
        if v is None or i is None:
            return
        ts = time.time()
        p = v * i
        self.reading_ready.emit(v, i, p, ts)

        # Ask the device first if it knows trip flags, then check locally
        # anyway. Two layers are cheap here.
        state = self.protection
        hw_trip = ""
        if state.hw_ovp_trip:
            r = self._exec("ovp_tripped")
            if r and r.strip().startswith("1"):
                hw_trip = "OVP"
        if not hw_trip and state.hw_ocp_trip:
            r = self._exec("ocp_tripped")
            if r and r.strip().startswith("1"):
                hw_trip = "OCP"
        if hw_trip and self._trip_reported != hw_trip:
            self._trip_reported = hw_trip
            self._emergency(hw_trip, v if hw_trip == "OVP" else i, hardware=True)
            return

        sw = state.check(v, i, ts)
        if sw and self._trip_reported != sw[0]:
            self._trip_reported = sw[0]
            self._emergency(sw[0], sw[1], hardware=False)
            return

        self.mode_changed.emit(state.mode_hint(v, i))

    def _emergency(self, kind: str, value: float, hardware: bool) -> None:
        """Shut down without going through the queue, this already runs in the worker."""
        try:
            self._exec("output_off")
        except Exception as exc:
            self.log_message.emit("ERROR", f"Not-Aus fehlgeschlagen: {exc}")
        src = "Hardware" if hardware else "Software"
        self.log_message.emit("ALARM", f"{src}-{kind} ausgeloest bei {value:.3f}")
        self.protection.mark_tripped(kind)
        self.protection_tripped.emit(kind, value)
