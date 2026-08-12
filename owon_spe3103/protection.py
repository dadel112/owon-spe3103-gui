"""OVP and OCP. The device's own protection is used where available, the
watchdog in here runs regardless."""

from __future__ import annotations

import threading

from . import scpi_map

# An excursion longer than this is treated as a gap in the sample stream (port
# hiccup, reconnect) and does not count towards the trip delay.
MAX_SAMPLE_GAP_S = 1.0

# Time below the threshold pays the accumulated over-time back at this fraction
# of the rate at which it built up. Slower than it builds so that a load which
# keeps crossing the limit still adds up instead of cancelling itself out, fast
# enough that a single inrush peak is forgotten within a few samples.
DECAY_RATIO = 0.5


class ProtectionManager:
    """Keeps thresholds and delay, and decides during polling whether the output
    has to go off. Touched from two threads, hence the lock.
    """

    def __init__(self):
        self._lock = threading.Lock()
        self.ovp_value = scpi_map.OVP_MAX
        self.ocp_value = scpi_map.OCP_MAX
        self.ovp_enabled = False
        self.ocp_enabled = False
        self.delay_ms = 0
        self.hw_ovp = False
        self.hw_ocp = False
        self.hw_ovp_trip = False
        self.hw_ocp_trip = False
        self.tripped = ""
        self.i_setpoint = 0.0
        self.v_setpoint = 0.0
        # Time spent above the threshold, per kind. Integrated instead of
        # restarted, see check().
        self._over_time: dict[str, float] = {}
        self._last_ts: float | None = None

    # -- Configuration ------------------------------------------------
    @staticmethod
    def clamp_ovp(volt: float) -> float:
        """Clamp to 0-33 V."""
        return max(0.0, min(scpi_map.OVP_MAX, float(volt)))

    @staticmethod
    def clamp_ocp(amp: float) -> float:
        """Clamp to 0-11 A."""
        return max(0.0, min(scpi_map.OCP_MAX, float(amp)))

    def set_ovp(self, volt: float, enabled: bool) -> None:
        """Set the OVP threshold and whether it is armed."""
        with self._lock:
            self.ovp_value = self.clamp_ovp(volt)
            self.ovp_enabled = bool(enabled)
            self._over_time.pop("OVP", None)

    def set_ocp(self, amp: float, enabled: bool) -> None:
        """Set the OCP threshold and whether it is armed."""
        with self._lock:
            self.ocp_value = self.clamp_ocp(amp)
            self.ocp_enabled = bool(enabled)
            self._over_time.pop("OCP", None)

    def set_delay(self, ms: int) -> None:
        """Trip delay, 0-2000 ms."""
        with self._lock:
            self.delay_ms = max(0, min(2000, int(ms)))

    def set_hardware(self, ovp: bool, ocp: bool, ovp_trip: bool, ocp_trip: bool) -> None:
        """Take over what discovery found out about device-side protection."""
        with self._lock:
            self.hw_ovp = bool(ovp)
            self.hw_ocp = bool(ocp)
            self.hw_ovp_trip = bool(ovp_trip)
            self.hw_ocp_trip = bool(ocp_trip)

    # -- State ---------------------------------------------------------
    def mark_tripped(self, kind: str) -> None:
        """Record a trip. The state stays until the reset button is pressed."""
        with self._lock:
            self.tripped = kind
            self._over_time.clear()
            self._last_ts = None

    def is_latched(self) -> bool:
        """True while a trip is waiting to be acknowledged. The watchdog does not
        evaluate anything in that state, so the output has to stay off."""
        with self._lock:
            return bool(self.tripped)

    def reset(self) -> None:
        """Clear the trip state, called from the reset button and on connect."""
        with self._lock:
            self.tripped = ""
            self._over_time.clear()
            self._last_ts = None

    def wants_trip_query(self, kind: str) -> bool:
        """Whether the device-side trip flag is worth polling: only if discovery
        found the query and that protection is actually armed. Every query costs
        a round trip and delays the next measurement."""
        with self._lock:
            if kind == "OVP":
                return self.hw_ovp_trip and self.ovp_enabled
            return self.hw_ocp_trip and self.ocp_enabled

    def stage_text(self) -> str:
        """Status line shown in the GUI."""
        with self._lock:
            armed = [name for name, on in (("OVP", self.ovp_enabled),
                                           ("OCP", self.ocp_enabled)) if on]
            if not armed:
                return "nothing armed - no OVP/OCP protection active"
            hw = [name for name, on in (("OVP", self.hw_ovp and self.ovp_enabled),
                                        ("OCP", self.hw_ocp and self.ocp_enabled)) if on]
            state = f"armed: {'/'.join(armed)}"
            if self.tripped:
                state += f" - {self.tripped} TRIPPED, waiting for reset"
            if hw:
                trip = "with trip query" if (self.hw_ovp_trip or self.hw_ocp_trip) \
                    else "no trip query"
                return f"{state}; hardware {'/'.join(hw)} ({trip}) + software watchdog"
            return f"{state}; software watchdog only, limited by the poll interval"

    def set_setpoint_current(self, amp: float) -> None:
        """Remember the current setpoint, needed for the CV/CC guess."""
        with self._lock:
            self.i_setpoint = max(0.0, float(amp))

    def set_setpoint_voltage(self, volt: float) -> None:
        """Remember the voltage setpoint, used for the reachability warning."""
        with self._lock:
            self.v_setpoint = max(0.0, float(volt))

    def reachability_warnings(self) -> list[str]:
        """Thresholds the supply can never reach in normal operation. Such a
        threshold looks armed but can only ever fire on a real fault, which is
        exactly the case people get wrong when setting it up.
        """
        with self._lock:
            out = []
            if self.ovp_enabled:
                if self.ovp_value > scpi_map.V_MAX:
                    out.append(f"OVP {self.ovp_value:.2f} V is above the device rating "
                               f"({scpi_map.V_MAX:.0f} V) - it can only fire on a fault")
                elif self.v_setpoint and self.ovp_value > self.v_setpoint:
                    out.append(f"OVP {self.ovp_value:.2f} V is above the voltage setpoint "
                               f"({self.v_setpoint:.2f} V) - in CV mode it will not fire")
            if self.ocp_enabled:
                if self.ocp_value > scpi_map.I_MAX:
                    out.append(f"OCP {self.ocp_value:.2f} A is above the device rating "
                               f"({scpi_map.I_MAX:.0f} A) - it can only fire on a fault")
                elif self.i_setpoint and self.ocp_value >= self.i_setpoint:
                    out.append(f"OCP {self.ocp_value:.2f} A is at or above the current "
                               f"setpoint ({self.i_setpoint:.2f} A) - the supply limits at "
                               f"the setpoint in CC mode, so it will not fire")
            return out

    def mode_hint(self, volt: float, amp: float) -> str:
        """CV/CC is guessed by comparing measured against set current, the device
        does not report its mode."""
        with self._lock:
            limit = self.i_setpoint
        if amp <= 0.001 and volt <= 0.01:
            return "--"
        return "CC" if limit and amp >= limit * 0.98 else "CV"

    # -- Software watchdog ---------------------------------------------
    def check(self, volt: float, amp: float, ts: float) -> tuple[str, float] | None:
        """Check both thresholds. A returned (kind, value) means: shut down now.

        The time spent above a threshold is integrated rather than restarted on
        every sample below it: a load that oscillates around the limit used to
        reset the timer on each dip and never tripped at all. Time below the
        limit pays the accumulator back down at DECAY_RATIO of that rate, so a
        single inrush peak still does not kill the output.

        `ts` must come from a monotonic clock.
        """
        with self._lock:
            if self.tripped:
                return None
            gap = 0.0 if self._last_ts is None else ts - self._last_ts
            self._last_ts = ts
            if gap < 0.0 or gap > MAX_SAMPLE_GAP_S:
                gap = 0.0
            delay = self.delay_ms / 1000.0
            checks = (
                ("OVP", self.ovp_enabled, volt, self.ovp_value),
                ("OCP", self.ocp_enabled, amp, self.ocp_value),
            )
            for kind, enabled, value, limit in checks:
                if not enabled:
                    self._over_time.pop(kind, None)
                    continue
                acc = self._over_time.get(kind, 0.0)
                if value > limit:
                    acc += gap
                    self._over_time[kind] = acc
                    if acc >= delay:
                        return kind, value
                else:
                    acc -= gap * DECAY_RATIO
                    if acc <= 0.0:
                        self._over_time.pop(kind, None)
                    else:
                        self._over_time[kind] = acc
        return None
