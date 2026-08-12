"""Watchdog logic, no Qt and no device needed.

Run with `python -m pytest tests` or plain `python tests/test_protection.py`.
Timestamps are fed in by hand, so the whole thing runs instantly.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from owon_spe3103.protection import ProtectionManager   # noqa: E402

POLL = 0.25     # the default poll interval


def armed(delay_ms: int = 0) -> ProtectionManager:
    """OCP armed at 2 A, everything else off."""
    prot = ProtectionManager()
    prot.set_ocp(2.0, True)
    prot.set_delay(delay_ms)
    return prot


def feed(prot: ProtectionManager, amps, t0: float = 0.0):
    """Push a series of current readings, one poll interval apart."""
    t = t0
    result = None
    for amp in amps:
        t += POLL
        result = result or prot.check(5.0, amp, t)
    return result


def test_trips_without_delay():
    prot = armed(0)
    assert feed(prot, [1.0]) is None
    assert feed(prot, [2.5]) == ("OCP", 2.5)


def test_short_peak_survives_the_delay():
    prot = armed(500)
    assert feed(prot, [1.0, 2.5, 1.0]) is None


def test_sustained_overload_trips():
    prot = armed(500)
    assert feed(prot, [1.0, 2.5, 2.5, 2.5]) == ("OCP", 2.5)


def test_oscillating_load_still_trips():
    """A load crossing the limit back and forth used to reset the timer on every
    dip and never tripped at all."""
    prot = armed(500)
    assert feed(prot, [1.0] + [2.5, 1.9] * 10) is not None


def test_gap_in_the_sample_stream_is_not_counted():
    """After a reconnect the missing seconds must not count as overload time."""
    prot = armed(500)
    prot.check(5.0, 1.0, 0.0)
    assert prot.check(5.0, 2.5, 60.0) is None


def test_latched_trip_blocks_further_checks_until_reset():
    prot = armed(0)
    prot.mark_tripped("OCP")
    assert prot.is_latched()
    assert prot.check(5.0, 9.0, 1.0) is None
    prot.reset()
    assert not prot.is_latched()
    assert feed(prot, [1.0, 9.0]) == ("OCP", 9.0)


def test_disarming_forgets_the_excursion():
    prot = armed(500)
    feed(prot, [2.5, 2.5])
    prot.set_ocp(2.0, False)
    prot.set_ocp(2.0, True)
    assert feed(prot, [2.5]) is None


def test_unreachable_thresholds_are_reported():
    prot = ProtectionManager()
    prot.set_setpoint_voltage(12.0)
    prot.set_setpoint_current(1.0)
    prot.set_ovp(30.0, True)     # above the setpoint, cannot fire in CV
    prot.set_ocp(5.0, True)      # above the setpoint, cannot fire in CC
    assert len(prot.reachability_warnings()) == 2
    prot.set_ovp(11.0, True)
    prot.set_ocp(0.8, True)
    assert prot.reachability_warnings() == []


def test_stage_text_reflects_what_is_armed():
    prot = ProtectionManager()
    assert "nothing armed" in prot.stage_text()
    prot.set_ovp(11.0, True)
    assert "armed: OVP" in prot.stage_text()


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"ok  {name}")
    print("all tests passed")
