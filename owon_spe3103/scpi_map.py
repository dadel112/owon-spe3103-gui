"""Every SCPI string used by this program. Candidates are unverified, discovery picks."""

# There is no reliable command reference for the SPE3103, so each function lists
# several plausible spellings. Known-good commands belong here and only here,
# otherwise SCPI ends up scattered across the codebase again.
COMMANDS = {
    "idn":            ["*IDN?"],
    "measure_volt":   ["MEAS:VOLT?", "MEASure:VOLTage?"],
    "measure_curr":   ["MEAS:CURR?", "MEASure:CURRent?"],
    "measure_power":  ["MEAS:POW?"],
    "set_volt":       ["VOLT {v}", "SOUR:VOLT {v}"],
    "set_curr":       ["CURR {i}", "SOUR:CURR {i}"],
    "get_volt_set":   ["VOLT?", "SOUR:VOLT?"],
    "get_curr_set":   ["CURR?", "SOUR:CURR?"],
    "output_on":      ["OUTP ON", "OUTP 1"],
    "output_off":     ["OUTP OFF", "OUTP 0"],
    "output_state":   ["OUTP?"],
    "ovp_set":        ["VOLT:PROT {v}", "VOLT:LIM {v}", "SOUR:VOLT:PROT {v}"],
    "ovp_get":        ["VOLT:PROT?", "VOLT:LIM?"],
    "ovp_enable":     ["VOLT:PROT:STAT ON", "VOLT:PROT:STAT 1"],
    "ovp_disable":    ["VOLT:PROT:STAT OFF", "VOLT:PROT:STAT 0"],
    "ovp_tripped":    ["VOLT:PROT:TRIP?"],
    "ocp_set":        ["CURR:PROT {i}", "CURR:LIM {i}", "SOUR:CURR:PROT {i}"],
    "ocp_get":        ["CURR:PROT?", "CURR:LIM?"],
    "ocp_enable":     ["CURR:PROT:STAT ON", "CURR:PROT:STAT 1"],
    "ocp_disable":    ["CURR:PROT:STAT OFF", "CURR:PROT:STAT 0"],
    "ocp_tripped":    ["CURR:PROT:TRIP?"],
    "prot_clear":     ["OUTP:PROT:CLE", "*CLS"],
    "system_error":   ["SYST:ERR?"],
    "remote":         ["SYST:REM"],
    "local":          ["SYST:LOC"],
}

# These go out via query(), everything else is write-only.
QUERY_KEYS = {
    "idn", "measure_volt", "measure_curr", "measure_power",
    "get_volt_set", "get_curr_set", "output_state",
    "ovp_get", "ocp_get", "ovp_tripped", "ocp_tripped", "system_error",
}

# How discovery verifies that a set command actually took effect.
READBACK = {
    "set_volt": "get_volt_set",
    "set_curr": "get_curr_set",
    "ovp_set":  "ovp_get",
    "ocp_set":  "ocp_get",
}

# Harmless probe values. The output is off while these are sent.
PROBE_ARGS = {
    "set_volt": {"v": 1.0},
    "set_curr": {"i": 0.5},
    "ovp_set":  {"v": 5.0},
    "ocp_set":  {"i": 1.0},
}

# SPE3103 nameplate ratings, plus some headroom for the protection thresholds.
V_MAX = 30.0
I_MAX = 10.0
OVP_MAX = 33.0
OCP_MAX = 11.0


def render(template: str, **kwargs) -> str:
    """Fill {v}/{i} into a candidate."""
    return template.format(**{k: f"{val:.3f}" if isinstance(val, float) else val
                              for k, val in kwargs.items()})


def candidates(key: str) -> list:
    """Candidate list for one function."""
    return list(COMMANDS.get(key, []))


def is_query(key: str) -> bool:
    """True if the function expects a response."""
    return key in QUERY_KEYS
