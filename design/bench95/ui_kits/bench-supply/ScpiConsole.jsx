/* SCPI console — the raw command line onto the instrument. */
function ScpiConsole({ ds, state, dispatch }) {
  const { Window, TextField, Button, StatusBar, Checkbox, Icon } = ds;
  const [cmd, setCmd] = React.useState("MEAS:VOLT?");
  const wellRef = React.useRef(null);
  React.useEffect(() => {
    if (wellRef.current) wellRef.current.scrollTop = wellRef.current.scrollHeight;
  }, [state.console.length]);
  return (
    <Window title="SCPI console" icon="code" width={420} onButton={(b) => dispatch({ type: "windowButton", target: "scpi", button: b })}>
      <div style={{ padding: "var(--space-8)", display: "flex", flexDirection: "column", gap: "var(--space-6)" }}>
        <div
          ref={wellRef}
          style={{
            height: 168,
            overflowY: "auto",
            background: "var(--surface-readout)",
            boxShadow: "var(--bevel-in)",
            padding: "var(--space-4) var(--space-6)",
            font: "var(--type-terminal)",
          }}
        >
          {state.console.map((l, i) => (
            <div key={i} style={{ color: l.dir === "tx" ? "var(--led-green)" : l.dir === "err" ? "var(--led-red)" : "var(--grey-100)", whiteSpace: "pre-wrap" }}>
              {l.dir === "tx" ? ">> " : l.dir === "err" ? "!! " : "<< "}
              {l.text}
            </div>
          ))}
        </div>
        <div style={{ display: "flex", gap: "var(--space-6)" }}>
          <TextField value={cmd} onChange={setCmd} mono style={{ flex: 1 }} />
          <Button isDefault onClick={() => { dispatch({ type: "send", text: cmd }); }}>Send</Button>
        </div>
        <div style={{ display: "flex", gap: "var(--space-16)", alignItems: "center" }}>
          <Checkbox checked label="Append newline" />
          <Checkbox checked={false} label="Echo timestamps" />
          <span style={{ marginLeft: "auto", display: "flex", alignItems: "center", gap: "var(--space-4)", font: "var(--type-label)", color: "var(--grey-700)" }}>
            <Icon name="info-box" size={16} /> Ctrl+↑ recalls history
          </span>
        </div>
      </div>
      <StatusBar panes={[state.connected ? "Connected" : "Not connected", { text: `${state.console.length} lines`, width: 78 }, { text: state.port, width: 70 }]} />
    </Window>
  );
}
Object.assign(window, { ScpiConsole });
