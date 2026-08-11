"""OVP/OCP-Logik: Hardware-Schutz plus stets aktiver Software-Fallback."""

from __future__ import annotations

import threading

from . import scpi_map


class ProtectionManager:
    """Schwellen, Ansprechverzoegerung und Software-Ueberwachung."""

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

    # -- Konfiguration ------------------------------------------------
    @staticmethod
    def clamp_ovp(volt: float) -> float:
        """Klemmt auf 0-33 V."""
        return max(0.0, min(scpi_map.OVP_MAX, float(volt)))

    @staticmethod
    def clamp_ocp(amp: float) -> float:
        """Klemmt auf 0-11 A."""
        return max(0.0, min(scpi_map.OCP_MAX, float(amp)))

    def set_ovp(self, volt: float, enabled: bool) -> None:
        """Setzt OVP-Schwelle und Freigabe."""
        with self._lock:
            self.ovp_value = self.clamp_ovp(volt)
            self.ovp_enabled = bool(enabled)
            self._over_since.pop("OVP", None)

    def set_ocp(self, amp: float, enabled: bool) -> None:
        """Setzt OCP-Schwelle und Freigabe."""
        with self._lock:
            self.ocp_value = self.clamp_ocp(amp)
            self.ocp_enabled = bool(enabled)
            self._over_since.pop("OCP", None)

    def set_delay(self, ms: int) -> None:
        """Ansprechverzoegerung 0-2000 ms."""
        with self._lock:
            self.delay_ms = max(0, min(2000, int(ms)))

    def set_hardware(self, ovp: bool, ocp: bool, ovp_trip: bool, ocp_trip: bool) -> None:
        """Uebernimmt das Discovery-Ergebnis zur Hardware-Unterstuetzung."""
        with self._lock:
            self.hw_ovp = bool(ovp)
            self.hw_ocp = bool(ocp)
            self.hw_ovp_trip = bool(ovp_trip)
            self.hw_ocp_trip = bool(ocp_trip)

    # -- Zustand ------------------------------------------------------
    def mark_tripped(self, kind: str) -> None:
        """Merkt eine Ausloesung; Reset nur explizit."""
        with self._lock:
            self.tripped = kind
            self._over_since.clear()

    def reset(self) -> None:
        """Loescht den Trip-Zustand (Button 'Schutz zuruecksetzen')."""
        with self._lock:
            self.tripped = ""
            self._over_since.clear()

    def stage_text(self) -> str:
        """Statuszeile fuer das GUI."""
        with self._lock:
            hw = []
            if self.hw_ovp:
                hw.append("OVP")
            if self.hw_ocp:
                hw.append("OCP")
            if hw:
                trip = "mit Trip-Abfrage" if (self.hw_ovp_trip or self.hw_ocp_trip) \
                    else "ohne Trip-Abfrage"
                return f"Hardware-{'/'.join(hw)} aktiv ({trip}) + Software-Ueberwachung"
            return "nur Software-Ueberwachung (Polling-begrenzt)"

    def set_setpoint_current(self, amp: float) -> None:
        """Merkt den Strom-Sollwert fuer die CV/CC-Ableitung."""
        with self._lock:
            self.i_setpoint = max(0.0, float(amp))

    def mode_hint(self, volt: float, amp: float) -> str:
        """Grobe CV/CC-Ableitung aus Messwert und Strom-Sollwert."""
        with self._lock:
            limit = self.i_setpoint
        if amp <= 0.001 and volt <= 0.01:
            return "--"
        return "CC" if limit and amp >= limit * 0.98 else "CV"

    # -- Software-Ueberwachung ---------------------------------------
    def check(self, volt: float, amp: float, ts: float) -> tuple[str, float] | None:
        """Prueft beide Schwellen; liefert (typ, wert) wenn abgeschaltet werden muss."""
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
