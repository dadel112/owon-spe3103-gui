"""Zentrale SCPI-Befehlstabelle. Kandidaten unverifiziert. Discovery entscheidet zur Laufzeit."""

# Fuer das SPE3103 gibt es keine verlaessliche Befehlsreferenz, deshalb pro Funktion
# mehrere plausible Schreibweisen. Wer sein Geraet kennt, traegt hier ein was wirklich
# geht - und nur hier, sonst steht am Ende wieder ueberall SCPI im Code herum.
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

# Alles hier drin wird per query() geschickt, der Rest ist reines Schreiben.
QUERY_KEYS = {
    "idn", "measure_volt", "measure_curr", "measure_power",
    "get_volt_set", "get_curr_set", "output_state",
    "ovp_get", "ocp_get", "ovp_tripped", "ocp_tripped", "system_error",
}

# Womit die Discovery nachprueft, ob ein Set-Befehl tatsaechlich angekommen ist.
READBACK = {
    "set_volt": "get_volt_set",
    "set_curr": "get_curr_set",
    "ovp_set":  "ovp_get",
    "ocp_set":  "ocp_get",
}

# Harmlose Werte zum Antesten. Der Ausgang ist dabei aus, es passiert also nichts.
PROBE_ARGS = {
    "set_volt": {"v": 1.0},
    "set_curr": {"i": 0.5},
    "ovp_set":  {"v": 5.0},
    "ocp_set":  {"i": 1.0},
}

# Typenschild des SPE3103, plus etwas Luft nach oben fuer die Schutzschwellen.
V_MAX = 30.0
I_MAX = 10.0
OVP_MAX = 33.0
OCP_MAX = 11.0


def render(template: str, **kwargs) -> str:
    """Setzt {v}/{i} in einen Kandidaten ein."""
    return template.format(**{k: f"{val:.3f}" if isinstance(val, float) else val
                              for k, val in kwargs.items()})


def candidates(key: str) -> list:
    """Kandidatenliste einer Funktion."""
    return list(COMMANDS.get(key, []))


def is_query(key: str) -> bool:
    """True wenn die Funktion eine Antwort erwartet."""
    return key in QUERY_KEYS
