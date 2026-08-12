"""OVP and OCP. The device's own protection is used where available, the
watchdog in here runs regardless."""

from __future__ import annotations

import threading

from . import scpi_map


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
        self._over_since: dict[str, float] = {}

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
            self._over_since.pop("OVP", None)

    def set_ocp(self, amp: float, enabled: bool) -> None:
        """Set the OCP threshold and whether it is armed."""
        with self._lock:
            self.ocp_value = self.clamp_ocp(amp)
            self.ocp_enabled = bool(enabled)
            self._over_since.pop("OCP", None)

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
            self._over_since.clear()

    def reset(self) -> None:
        """Clear the trip state, called from the reset button."""
        with self._lock:
            self.tripped = ""
            self._over_since.clear()

    def stage_text(self) -> str:
        """Status line shown in the GUI."""
        with self._lock:
            hw = []
            if self.hw_ovp:
                hw.append("OVP")
            if self.hw_ocp:
                hw.append("OCP")
            if hw:
                trip = "with trip query" if (self.hw_ovp_trip or self.hw_ocp_trip) \
                    else "no trip query"
                return f"hardware {'/'.join(hw)} active ({trip}) + software watchdog"
            return "software watchdog only, limited by the poll interval"

    def set_setpoint_current(self, amp: float) -> None:
        """Remember the current setpoint, needed for the CV/CC guess."""
        with self._lock:
            self.i_setpoint = max(0.0, float(amp))

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
        An excursion has to persist for the configured delay so that an inrush
        peak does not kill the output right away.
        """
        with self._lock:
            if self.tripped:
                return None
            delay = self.delay_ms / 1000.0
            checks = (
                ("OVP", self.ovp_enabled, volt, self.ovp_value),
                ("OCP", self.ocp_enabled, amp, self.ocp_value),
            )
            for kind, enabled, value, limit in checks:
                if not enabled or value <= limit:
                    self._over_since.pop(kind, None)
                    continue
                start = self._over_since.setdefault(kind, ts)
                if ts - start >= delay:
                    return kind, value
        return None
