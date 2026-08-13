/* Bench95 Supply — main control window. Loaded as text/babel; publishes to window. */
function MainWindow({ ds, state, dispatch }) {
  const { Window, MenuBar, Toolbar, ToolbarGrip, ToolbarSeparator, IconButton, Panel, Button, NumberSpinner, Slider, Checkbox, Radio, LedReadout, Led, StatusBar, Tooltip } = ds;
  const { connected, output, setV, setI, meas, mode, ovp, ocp, ovpLevel, tripped, port } = state;

  const menus = [
    { label: "File", items: [{ label: "Open Profile…", shortcut: "Ctrl+O" }, { label: "Save Profile", shortcut: "Ctrl+S" }, "-", { label: "Export Log…", disabled: !connected }, "-", { label: "Exit" }] },
    { label: "Device", items: [{ label: "Connect…", disabled: connected }, { label: "Disconnect", disabled: !connected }, "-", { label: "Reset Device", disabled: !connected }, { label: "Clear Trip", disabled: !tripped }] },
    { label: "View", items: [{ label: "Sequence Editor" }, { label: "Data Log" }, { label: "SCPI Console" }] },
    { label: "Help", items: [{ label: "About Bench95 Supply" }] },
  ];

  return (
    <Window title={`Bench95 Supply — ${connected ? port : "not connected"}`} icon="zap" width={648} onButton={(b) => dispatch({ type: "windowButton", target: "main", button: b })}>
      <MenuBar menus={menus} onSelect={(m, i) => dispatch({ type: "menu", menu: m, item: i })} />
      <Toolbar>
        <ToolbarGrip />
        <Tooltip text={connected ? "Disconnect" : "Connect to device (F2)"}>
          <IconButton icon="power" label="Connect" active={connected} onClick={() => dispatch({ type: connected ? "disconnect" : "openConnect" })} />
        </Tooltip>
        <Tooltip text="Output enable (F5)"><IconButton icon="zap" label="Output" active={output} disabled={!connected} onClick={() => dispatch({ type: "toggleOutput" })} /></Tooltip>
        <ToolbarSeparator />
        <Tooltip text="Read setpoints from device"><IconButton icon="reload" label="Read" disabled={!connected} onClick={() => dispatch({ type: "read" })} /></Tooltip>
        <Tooltip text="Save profile (Ctrl+S)"><IconButton icon="save" label="Save profile" /></Tooltip>
        <ToolbarSeparator />
        <Tooltip text="Sequence editor"><IconButton icon="sliders" label="Sequence" active={state.windows.sequence} onClick={() => dispatch({ type: "openWindow", id: "sequence" })} /></Tooltip>
        <Tooltip text="Data log"><IconButton icon="chart" label="Log" active={state.windows.log} onClick={() => dispatch({ type: "openWindow", id: "log" })} /></Tooltip>
        <Tooltip text="SCPI console"><IconButton icon="code" label="Console" active={state.windows.scpi} onClick={() => dispatch({ type: "openWindow", id: "scpi" })} /></Tooltip>
      </Toolbar>

      <div style={{ display: "flex", gap: "var(--space-8)", padding: "var(--space-8)", alignItems: "flex-start" }}>
        <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-8)", flex: "0 0 auto" }}>
          <Panel label="Measured" bodyStyle={{ display: "flex", flexDirection: "column", gap: "var(--space-4)" }}>
            <LedReadout label="VOLTS" value={meas.v} digits={3} unit="V" size="lg" off={!output} style={{ width: 232 }} />
            <div style={{ display: "flex", gap: "var(--space-4)" }}>
              <LedReadout label="AMPS" value={meas.i} digits={3} unit="A" color="amber" off={!output} style={{ flex: 1 }} />
              <LedReadout label="WATTS" value={meas.v * meas.i} digits={2} unit="W" size="sm" off={!output} style={{ flex: 1 }} />
            </div>
            <div style={{ display: "flex", gap: "var(--space-16)", paddingTop: "var(--space-4)" }}>
              <Led on={connected} label="LINK" />
              <Led on={output && mode === "CC"} color="amber" label="CC" />
              <Led on={tripped} color="red" blink label="TRIP" />
            </div>
          </Panel>
          <Button icon="power" block disabled={!connected} pressed={output} onClick={() => dispatch({ type: "toggleOutput" })} style={{ height: 30, fontWeight: "var(--weight-bold)" }}>
            {output ? "OUTPUT ON — click to disable" : "OUTPUT OFF — click to enable"}
          </Button>
        </div>

        <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-8)", flex: "1 1 auto", minWidth: 0 }}>
          <Panel label="Setpoints">
            <div style={{ display: "grid", gridTemplateColumns: "auto 1fr", gap: "var(--space-6) var(--space-8)", alignItems: "center" }}>
              <span>Voltage</span>
              <div style={{ display: "flex", gap: "var(--space-6)", alignItems: "center" }}>
                <NumberSpinner value={setV} onChange={(v) => dispatch({ type: "setV", value: v })} step={0.1} max={30} decimals={3} unit="V" width={92} />
                <Slider value={setV} min={0} max={30} step={0.1} ticks={7} onChange={(v) => dispatch({ type: "setV", value: v })} width={132} />
              </div>
              <span>Current</span>
              <div style={{ display: "flex", gap: "var(--space-6)", alignItems: "center" }}>
                <NumberSpinner value={setI} onChange={(v) => dispatch({ type: "setI", value: v })} step={0.01} max={5} decimals={3} unit="A" width={92} />
                <Slider value={setI} min={0} max={5} step={0.01} ticks={6} onChange={(v) => dispatch({ type: "setI", value: v })} width={132} />
              </div>
            </div>
          </Panel>
          <Panel label="Protection">
            <div style={{ display: "flex", gap: "var(--space-16)" }}>
              <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-4)" }}>
                <Checkbox checked={ovp} onChange={(c) => dispatch({ type: "set", key: "ovp", value: c })} label="OVP" />
                <Checkbox checked={ocp} onChange={(c) => dispatch({ type: "set", key: "ocp", value: c })} label="OCP" />
                <Checkbox checked={false} disabled label="Remote sense" />
              </div>
              <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-4)" }}>
                <NumberSpinner value={ovpLevel} onChange={(v) => dispatch({ type: "set", key: "ovpLevel", value: v })} step={0.5} max={33} decimals={2} unit="V" width={92} disabled={!ovp} />
                <NumberSpinner value={5.5} step={0.1} max={5.5} decimals={2} unit="A" width={92} disabled={!ocp} />
              </div>
            </div>
          </Panel>
          <Panel label="Regulation">
            <div style={{ display: "flex", gap: "var(--space-16)" }}>
              <Radio name="mode" checked={mode === "CV"} onChange={() => dispatch({ type: "set", key: "mode", value: "CV" })} label="Constant voltage" />
              <Radio name="mode" checked={mode === "CC"} onChange={() => dispatch({ type: "set", key: "mode", value: "CC" })} label="Constant current" />
            </div>
          </Panel>
        </div>
      </div>

      <StatusBar
        panes={[
          tripped ? { text: "OVP tripped — output latched off", tone: "danger" } : connected ? (output ? "Output enabled" : "Ready") : "Not connected",
          { text: mode, width: 36 },
          { text: connected ? `${port} · 9600 8N1` : "—", width: 118 },
          { text: "PSU-3005", width: 74 },
        ]}
      />
    </Window>
  );
}
Object.assign(window, { MainWindow });
