/* Desktop shell + app state for the Bench95 Supply kit. */
const START_STEPS = [
  { v: 3.3, i: 0.5, dwell: 5, note: "logic rail" },
  { v: 5.0, i: 1.0, dwell: 10, note: "usb rail" },
  { v: 12.0, i: 1.25, dwell: 30, note: "fan + load" },
  { v: 24.0, i: 2.0, dwell: 15, note: "motor stall" },
  { v: 0.0, i: 0.0, dwell: 2, note: "settle" },
];

/* a plausible minute of history so the log window is never empty */
function seedSamples() {
  const out = [];
  const t0 = Date.now() - 60000;
  for (let k = 0; k < 60; k++) {
    const v = k < 8 ? 0 : k < 20 ? 5 + Math.random() * 0.02 : k < 44 ? 12 + Math.random() * 0.03 : 23.98 + Math.random() * 0.04;
    const i = k < 8 ? 0 : k < 20 ? 0.51 : k < 44 ? 1.25 : 2.02;
    out.push({ t: new Date(t0 + k * 1000).toLocaleTimeString("en-GB", { hour12: false }), v, i, mode: k >= 44 ? "CC" : "CV" });
  }
  return out;
}

const initialState = {
  booted: false,
  connected: false,
  port: "COM3",
  output: false,
  setV: 12.0,
  setI: 1.25,
  meas: { v: 0, i: 0 },
  mode: "CV",
  ovp: true,
  ocp: false,
  ovpLevel: 13.5,
  tripped: false,
  steps: START_STEPS,
  seqRunning: false,
  seqIndex: 0,
  seqProgress: 0,
  logging: true,
  interval: "1 s",
  samples: seedSamples(),
  console: [
    { dir: "rx", text: "bench95 0.9.2 — python 3.11" },
    { dir: "rx", text: "no device attached" },
  ],
  windows: { main: false, sequence: false, log: false, scpi: false },
  connectOpen: true,
  dialog: null,
  active: "main",
};

const now = () => new Date().toLocaleTimeString("en-GB", { hour12: false });

function reducer(s, a) {
  switch (a.type) {
    case "connect":
      return {
        ...s,
        connected: true,
        port: a.port,
        connectOpen: false,
        windows: { ...s.windows, main: true },
        active: "main",
        console: [...s.console, { dir: "tx", text: "*IDN?" }, { dir: "rx", text: "BENCH,PSU-3005,SN20240117,FW1.42" }],
      };
    case "openConnect":
      return { ...s, connectOpen: true };
    case "closeConnect":
      return { ...s, connectOpen: false, windows: { ...s.windows, main: true } };
    case "disconnect":
      if (s.output) return { ...s, dialog: { kind: "warning", title: "Bench95 Supply", message: "Output is still enabled.", detail: "Disable the output before disconnecting the load.", buttons: ["Disable and disconnect", "Cancel"], onOk: "forceDisconnect" } };
      return { ...s, connected: false, output: false, meas: { v: 0, i: 0 }, console: [...s.console, { dir: "rx", text: "port closed" }] };
    case "forceDisconnect":
      return { ...s, connected: false, output: false, tripped: false, meas: { v: 0, i: 0 }, dialog: null, console: [...s.console, { dir: "tx", text: "OUTP OFF" }, { dir: "rx", text: "port closed" }] };
    case "toggleOutput": {
      if (!s.connected) return s;
      if (s.tripped) return { ...s, dialog: { kind: "error", title: "Protection", message: "OVP is latched.", detail: "Clear the trip from the Device menu before enabling the output.", buttons: ["OK"] } };
      const output = !s.output;
      return { ...s, output, meas: output ? { v: s.setV, i: s.setI } : { v: 0, i: 0 }, console: [...s.console, { dir: "tx", text: `OUTP ${output ? "ON" : "OFF"}` }] };
    }
    case "setV": {
      const tripped = s.ovp && a.value > s.ovpLevel;
      return { ...s, setV: a.value, tripped: tripped ? true : s.tripped, output: tripped ? false : s.output, meas: tripped ? { v: 0, i: 0 } : s.meas, console: [...s.console, { dir: "tx", text: `VOLT ${a.value.toFixed(3)}` }, ...(tripped ? [{ dir: "err", text: "OVP tripped, output latched off" }] : [])] };
    }
    case "setI":
      return { ...s, setI: a.value, console: [...s.console, { dir: "tx", text: `CURR ${a.value.toFixed(3)}` }] };
    case "set":
      return { ...s, [a.key]: a.value };
    case "read":
      return { ...s, console: [...s.console, { dir: "tx", text: "VOLT?;CURR?" }, { dir: "rx", text: `${s.setV.toFixed(3)};${s.setI.toFixed(3)}` }] };
    case "send": {
      const t = a.text.trim().toUpperCase();
      const reply = t.includes("MEAS:VOLT") ? s.meas.v.toFixed(4) : t.includes("MEAS:CURR") ? s.meas.i.toFixed(4) : t.includes("*IDN") ? "BENCH,PSU-3005,SN20240117,FW1.42" : t.endsWith("?") ? "0" : "OK";
      if (!s.connected) return { ...s, console: [...s.console, { dir: "tx", text: a.text }, { dir: "err", text: "not connected" }] };
      return { ...s, console: [...s.console, { dir: "tx", text: a.text }, { dir: "rx", text: reply }] };
    }
    case "clearTrip":
      return { ...s, tripped: false, console: [...s.console, { dir: "tx", text: "OUTP:PROT:CLE" }] };
    case "openWindow":
      return { ...s, windows: { ...s.windows, [a.id]: true }, active: a.id };
    case "windowButton":
      if (a.button === "close") {
        if (a.target === "main") return { ...s, windows: { ...s.windows, main: false }, connectOpen: false };
        return { ...s, windows: { ...s.windows, [a.target]: false } };
      }
      return { ...s, active: a.target };
    case "focus":
      return { ...s, active: a.id, windows: { ...s.windows, [a.id]: true } };
    case "editStep": {
      const steps = s.steps.map((st, i) => (i === a.index ? { ...st, [a.key]: a.value } : st));
      return { ...s, steps };
    }
    case "runSequence":
      return { ...s, seqRunning: true, seqIndex: 0, seqProgress: 0, output: true, meas: { v: s.steps[0].v, i: s.steps[0].i }, console: [...s.console, { dir: "tx", text: "run ramp_test.b95" }] };
    case "stopSequence":
      return { ...s, seqRunning: false, seqProgress: 0 };
    case "seqTick": {
      if (!s.seqRunning) return s;
      const p = s.seqProgress + 4;
      if (p >= 100) return { ...s, seqRunning: false, seqProgress: 100, output: false, meas: { v: 0, i: 0 } };
      const idx = Math.min(s.steps.length - 1, Math.floor((p / 100) * s.steps.length));
      const st = s.steps[idx];
      return { ...s, seqProgress: p, seqIndex: idx, meas: { v: st.v, i: st.i } };
    }
    case "toggleLogging":
      return { ...s, logging: !s.logging };
    case "clearLog":
      return { ...s, samples: [] };
    case "sample": {
      if (!s.logging) return s;
      const jitter = (n) => n * (1 + (Math.random() - 0.5) * 0.004);
      const v = s.output ? jitter(s.meas.v) : 0;
      const i = s.output ? jitter(s.meas.i) : 0;
      return { ...s, samples: [...s.samples, { t: now(), v, i, mode: s.mode }].slice(-240), meas: s.output ? { v, i } : s.meas };
    }
    case "menu": {
      const item = a.item;
      if (item === "Connect…") return { ...s, connectOpen: true };
      if (item === "Disconnect") return reducer(s, { type: "disconnect" });
      if (item === "Clear Trip") return reducer(s, { type: "clearTrip" });
      if (item === "Sequence Editor") return reducer(s, { type: "openWindow", id: "sequence" });
      if (item === "Data Log") return reducer(s, { type: "openWindow", id: "log" });
      if (item === "SCPI Console") return reducer(s, { type: "openWindow", id: "scpi" });
      if (item === "Reset Device") return { ...s, dialog: { kind: "question", title: "Reset device", message: "Send *RST to the supply?", detail: "Setpoints return to 0.000 V / 0.000 A and the output is disabled.", buttons: ["OK", "Cancel"], onOk: "doReset" } };
      if (item === "About Bench95 Supply") return { ...s, dialog: { kind: "info", title: "About", message: "Bench95 Supply 0.9.2", detail: "Serial control for programmable bench supplies. Python 3.11 · pyserial 3.5 · Tk shell.", buttons: ["OK"] } };
      if (item === "Exit") return { ...s, windows: { main: false, sequence: false, log: false, scpi: false } };
      return { ...s, dialog: { kind: "info", title: item, message: `${item} is not part of this mock-up.`, buttons: ["OK"] } };
    }
    case "doReset":
      return { ...s, setV: 0, setI: 0, output: false, meas: { v: 0, i: 0 }, dialog: null, console: [...s.console, { dir: "tx", text: "*RST" }] };
    case "closeDialog":
      return { ...s, dialog: null };
    case "boot":
      return { ...s, booted: true };
    default:
      return s;
  }
}

function DesktopIcon({ ds, icon, label, onOpen }) {
  const { Icon } = ds;
  const [sel, setSel] = React.useState(false);
  return (
    <button
      type="button"
      onClick={() => setSel(true)}
      onDoubleClick={onOpen}
      onBlur={() => setSel(false)}
      style={{ width: 72, border: 0, background: "transparent", display: "flex", flexDirection: "column", alignItems: "center", gap: "var(--space-4)", padding: "var(--space-4)", cursor: "default", color: "var(--grey-white)" }}
    >
      <span style={{ background: sel ? "var(--surface-selected)" : "transparent", padding: 2 }}>
        <Icon name={icon} size={32} color="#ffffff" />
      </span>
      <span style={{ font: "var(--type-label)", color: "var(--grey-white)", background: sel ? "var(--surface-selected)" : "transparent", textShadow: "1px 1px 0 rgba(0,0,0,.6)", padding: "0 2px", textAlign: "center" }}>{label}</span>
    </button>
  );
}

function Desktop({ ds }) {
  const [state, dispatch] = React.useReducer(reducer, initialState);
  const { TaskBar, Dialog } = ds;

  React.useEffect(() => {
    const t = setInterval(() => dispatch({ type: "sample" }), 900);
    return () => clearInterval(t);
  }, []);
  React.useEffect(() => {
    if (!state.seqRunning) return;
    const t = setInterval(() => dispatch({ type: "seqTick" }), 320);
    return () => clearInterval(t);
  }, [state.seqRunning]);

  const open = (id) => dispatch({ type: "focus", id });
  const tasks = [
    state.windows.main && { label: "Bench95 Supply", icon: "zap", id: "main" },
    state.windows.sequence && { label: "Sequence", icon: "sliders", id: "sequence" },
    state.windows.log && { label: "Data log", icon: "chart", id: "log" },
    state.windows.scpi && { label: "SCPI console", icon: "code", id: "scpi" },
  ].filter(Boolean);

  const z = (id) => (state.active === id ? 30 : 10);

  return (
    <div style={{ position: "absolute", inset: 0, display: "flex", flexDirection: "column", background: "var(--gradient-hill)", overflow: "hidden" }}>
      <div style={{ position: "relative", flex: 1, minHeight: 0 }}>
        <div style={{ position: "absolute", top: 8, left: 8, display: "flex", flexDirection: "column", gap: "var(--space-4)" }}>
          <DesktopIcon ds={ds} icon="zap" label="Bench95 Supply" onOpen={() => open("main")} />
          <DesktopIcon ds={ds} icon="sliders" label="Sequences" onOpen={() => open("sequence")} />
          <DesktopIcon ds={ds} icon="chart" label="Data log" onOpen={() => open("log")} />
          <DesktopIcon ds={ds} icon="code" label="SCPI console" onOpen={() => open("scpi")} />
        </div>

        {state.windows.main ? (
          <div onMouseDown={() => open("main")} style={{ position: "absolute", left: 96, top: 16, zIndex: z("main") }}>
            <MainWindow ds={ds} state={state} dispatch={dispatch} />
          </div>
        ) : null}
        {state.windows.sequence ? (
          <div onMouseDown={() => open("sequence")} style={{ position: "absolute", left: 286, top: 254, zIndex: z("sequence") }}>
            <SequenceWindow ds={ds} state={state} dispatch={dispatch} />
          </div>
        ) : null}
        {state.windows.log ? (
          <div onMouseDown={() => open("log")} style={{ position: "absolute", left: 626, top: 40, zIndex: z("log") }}>
            <LogWindow ds={ds} state={state} dispatch={dispatch} />
          </div>
        ) : null}
        {state.windows.scpi ? (
          <div onMouseDown={() => open("scpi")} style={{ position: "absolute", left: 132, top: 356, zIndex: z("scpi") }}>
            <ScpiConsole ds={ds} state={state} dispatch={dispatch} />
          </div>
        ) : null}

        {state.connectOpen ? (
          <div style={{ position: "absolute", left: 300, top: 150, zIndex: 50 }}>
            <ConnectDialog ds={ds} state={state} dispatch={dispatch} />
          </div>
        ) : null}

        {state.dialog ? (
          <div style={{ position: "absolute", left: 340, top: 220, zIndex: 60 }}>
            <Dialog
              {...state.dialog}
              onButton={(b) => {
                if (state.dialog.onOk && b === state.dialog.buttons[0]) dispatch({ type: state.dialog.onOk });
                else dispatch({ type: "closeDialog" });
              }}
            />
          </div>
        ) : null}
      </div>

      <TaskBar
        startLabel="Bench"
        tasks={tasks.map((t) => ({ label: t.label, icon: t.icon }))}
        activeTask={(tasks.find((t) => t.id === state.active) || {}).label}
        onTask={(label) => open((tasks.find((t) => t.label === label) || {}).id)}
        onStart={() => dispatch({ type: "menu", menu: "Help", item: "About Bench95 Supply" })}
        tray={["cellular-signal-3", "volume-3"]}
        clock={now().slice(0, 5)}
      />
    </div>
  );
}
Object.assign(window, { Desktop, reducer, initialState });
