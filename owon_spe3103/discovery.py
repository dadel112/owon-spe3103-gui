"""Laufzeit-Discovery der SCPI-Befehle.
Testet die Kandidaten aus scpi_map gegen das Geraet und speichert das
Ergebnis in scpi_profile.json neben main.py.
"""

from __future__ import annotations

import json
import os
import sys

from . import scpi_map

PROFILE_NAME = "scpi_profile.json"


def profile_path() -> str:
    """Pfad zu scpi_profile.json neben main.py."""
    base = os.path.dirname(os.path.abspath(sys.argv[0])) if sys.argv and sys.argv[0] else os.getcwd()
    return os.path.join(base, PROFILE_NAME)


class Discovery:
    """Ermittelt pro Funktion den ersten akzeptierten Kandidaten.
    Set-Befehle werden nur bei ausgeschaltetem Ausgang und mit Readback geprueft.
    """

    def __init__(self, transport, log=None):
        self._t = transport
        self._log = log or (lambda level, text: None)
        self._err_cmd = ""

    # -- Hilfen -------------------------------------------------------
    def _write(self, cmd: str) -> None:
        self._log("TX", cmd)
        self._t.write(cmd)

    def _query(self, cmd: str) -> str:
        self._log("TX", cmd)
        resp = self._t.query(cmd)
        self._log("RX", resp)
        return resp

    def _clear_errors(self) -> None:
        if not self._err_cmd:
            return
        for _ in range(5):
            try:
                if self._err_code(self._query(self._err_cmd)) == 0:
                    return
            except Exception:             # noqa: BLE001
                return

    @staticmethod
    def _err_code(resp: str) -> int:
        try:
            return int(float(resp.split(",")[0].strip()))
        except (ValueError, IndexError):
            return 0

    def _accepted(self) -> bool:
        """SYST:ERR? pollen; ohne Fehlerabfrage gilt 'kein Timeout' als Erfolg."""
        if not self._err_cmd:
            return True
        try:
            return self._err_code(self._query(self._err_cmd)) == 0
        except Exception:                 # noqa: BLE001
            return False

    @staticmethod
    def _is_number(resp: str) -> bool:
        try:
            float(resp.split(",")[0].strip())
            return True
        except (ValueError, IndexError):
            return False

    # -- Einzeltests --------------------------------------------------
    def _try_query(self, cand: str, numeric: bool) -> bool:
        try:
            resp = self._query(cand)
        except Exception:                 # noqa: BLE001
            self._clear_errors()
            return False
        if not resp:
            return False
        if numeric and not self._is_number(resp):
            self._clear_errors()
            return False
        return self._accepted()

    def _try_write(self, cand: str) -> bool:
        try:
            self._write(cand)
        except Exception:                 # noqa: BLE001
            self._clear_errors()
            return False
        return self._accepted()

    def _try_set(self, key: str, cand: str, profile: dict) -> bool:
        args = scpi_map.PROBE_ARGS.get(key, {})
        try:
            self._write(scpi_map.render(cand, **args))
        except Exception:                 # noqa: BLE001
            self._clear_errors()
            return False
        if not self._accepted():
            return False
        rb_key = scpi_map.READBACK.get(key)
        rb_cmd = profile.get(rb_key) if rb_key else None
        if not rb_cmd:
            return True                   # ohne Readback gilt Fehlerfreiheit
        try:
            value = float(self._query(rb_cmd).split(",")[0])
        except Exception:                 # noqa: BLE001
            self._clear_errors()
            return False
        target = float(next(iter(args.values()), 0.0))
        return abs(value - target) <= max(0.05, target * 0.02)

    # -- Ablauf -------------------------------------------------------
    def run(self, path: str, demo: bool = False) -> tuple[dict, str]:
        """Profil laden oder ermitteln. Liefert (profil, idn)."""
        idn = ""
        cached = None if demo else self._load(path)
        if cached:
            idn = cached.get("_idn", "")
            self._log("INFO", f"SCPI-Profil geladen: {os.path.basename(path)}")
            return {k: v for k, v in cached.items() if not k.startswith("_")}, idn

        profile: dict[str, str | None] = {}

        for cand in scpi_map.candidates("idn"):
            try:
                idn = self._query(cand)
                if idn:
                    profile["idn"] = cand
                    break
            except Exception:             # noqa: BLE001
                continue
        self._log("INFO", f"IDN: {idn or 'keine Antwort'}")

        for cand in scpi_map.candidates("system_error"):
            try:
                if self._query(cand):
                    profile["system_error"] = cand
                    self._err_cmd = cand
                    break
            except Exception:             # noqa: BLE001
                continue
        self._clear_errors()

        # Reihenfolge: erst Queries (Readback-Basis), dann Writes, dann Sets.
        query_keys = ["measure_volt", "measure_curr", "measure_power",
                      "get_volt_set", "get_curr_set", "output_state",
                      "ovp_get", "ocp_get", "ovp_tripped", "ocp_tripped"]
        write_keys = ["output_off", "output_on", "remote", "local",
                      "ovp_enable", "ovp_disable", "ocp_enable", "ocp_disable",
                      "prot_clear"]
        set_keys = ["set_volt", "set_curr", "ovp_set", "ocp_set"]

        for key in query_keys:
            profile[key] = self._first(key, lambda c: self._try_query(c, True))

        # Ausgang sicher aus, bevor Writes/Sets getestet werden.
        off = self._first("output_off", self._try_write)
        profile["output_off"] = off

        for key in write_keys:
            if key == "output_off":
                continue
            if key == "output_on":
                # Nur syntaktisch pruefen waere unsicher: Kandidat uebernehmen,
                # der zum akzeptierten output_off-Praefix passt.
                profile[key] = self._pair_with(key, off)
                continue
            profile[key] = self._first(key, self._try_write)

        for key in set_keys:
            profile[key] = self._first(key, lambda c, k=key: self._try_set(k, c, profile))

        missing = [k for k, v in profile.items() if not v]
        self._log("INFO", f"Discovery fertig, nicht unterstuetzt: {missing or 'keine'}")
        if not demo:
            self._save(path, profile, idn)
        return profile, idn

    def _first(self, key: str, test) -> str | None:
        for cand in scpi_map.candidates(key):
            if test(cand):
                self._log("INFO", f"{key}: '{cand}' akzeptiert")
                return cand
        self._log("WARN", f"{key}: kein Kandidat akzeptiert")
        return None

    @staticmethod
    def _pair_with(key: str, reference: str | None) -> str | None:
        """Nimmt den Kandidaten mit gleichem Index wie der akzeptierte Gegenbefehl."""
        cands = scpi_map.candidates(key)
        off = scpi_map.candidates("output_off")
        if not cands:
            return None
        if reference in off:
            idx = off.index(reference)
            if idx < len(cands):
                return cands[idx]
        return cands[0]

    # -- Persistenz ---------------------------------------------------
    def _load(self, path: str) -> dict | None:
        try:
            with open(path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            return data if isinstance(data, dict) else None
        except (OSError, ValueError):
            return None

    def _save(self, path: str, profile: dict, idn: str) -> None:
        data = dict(profile)
        data["_idn"] = idn
        try:
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(data, fh, indent=2)
            self._log("INFO", f"SCPI-Profil gespeichert: {os.path.basename(path)}")
        except OSError as exc:
            self._log("WARN", f"Profil nicht speicherbar: {exc}")
