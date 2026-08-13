/* Data log window — live trace, measurement table, CSV export. */
function LogWindow({ ds, state, dispatch }) {
  const { Window, Toolbar, ToolbarGrip, ToolbarSeparator, IconButton, PlotWell, ListView, StatusBar, Checkbox, Select, Tooltip, Led } = ds;
  const { samples, logging, interval } = state;
  const vMax = 30, iMax = 5;
  const vPts = samples.map((s, i) => ({ x: samples.length > 1 ? i / (samples.length - 1) : 0, y: s.v / vMax }));
  const iPts = samples.map((s, i) => ({ x: samples.length > 1 ? i / (samples.length - 1) : 0, y: s.i / iMax }));
  const rows = samples.slice(-40).reverse().map((s) => ({ t: s.t, v: s.v.toFixed(3), i: s.i.toFixed(3), w: (s.v * s.i).toFixed(2), m: s.mode }));
  return (
    <Window title="Data log" icon="chart" width={520} onButton={(b) => dispatch({ type: "windowButton", target: "log", button: b })}>
      <Toolbar>
        <ToolbarGrip />
        <Tooltip text={logging ? "Stop logging" : "Start logging"}><IconButton icon={logging ? "pause" : "play"} label="Log" active={logging} onClick={() => dispatch({ type: "toggleLogging" })} /></Tooltip>
        <Tooltip text="Clear log"><IconButton icon="trash" label="Clear" onClick={() => dispatch({ type: "clearLog" })} /></Tooltip>
        <ToolbarSeparator />
        <Tooltip text="Export CSV"><IconButton icon="download" label="Export CSV" /></Tooltip>
        <ToolbarSeparator />
        <span style={{ font: "var(--type-label)" }}>Interval</span>
        <Select value={interval} options={["0.2 s", "1 s", "5 s"]} onChange={(v) => dispatch({ type: "set", key: "interval", value: v })} width={72} />
        <span style={{ marginLeft: "auto", display: "flex", gap: "var(--space-8)" }}>
          <Led on={logging} label="REC" />
        </span>
      </Toolbar>
      <div style={{ padding: "var(--space-8)", display: "flex", flexDirection: "column", gap: "var(--space-6)" }}>
        <div style={{ display: "flex", gap: "var(--space-4)" }}>
          <div style={{ display: "flex", flexDirection: "column", justifyContent: "space-between", font: "var(--weight-normal) var(--text-xs)/1 var(--font-mono)", textAlign: "right", width: 26, padding: "2px 0" }}>
            <span>30 V</span><span>15</span><span>0</span>
          </div>
          <PlotWell height={132} style={{ flex: 1 }} series={[{ points: vPts }, { points: iPts, color: "var(--led-amber)" }]} />
        </div>
        <div style={{ display: "flex", gap: "var(--space-16)", font: "var(--type-label)", paddingLeft: 30 }}>
          <span style={{ display: "flex", alignItems: "center", gap: "var(--space-4)" }}><span style={{ width: 12, height: 2, background: "var(--led-green)" }} /> Volts</span>
          <span style={{ display: "flex", alignItems: "center", gap: "var(--space-4)" }}><span style={{ width: 12, height: 2, background: "var(--led-amber)" }} /> Amps</span>
          <Checkbox checked label="Autoscale" style={{ marginLeft: "auto" }} />
        </div>
        <ListView
          mono
          height={120}
          columns={[
            { key: "t", label: "Time", width: 72 },
            { key: "v", label: "Volts", align: "right", width: 66 },
            { key: "i", label: "Amps", align: "right", width: 66 },
            { key: "w", label: "Watts", align: "right", width: 66 },
            { key: "m", label: "Mode", width: 46 },
          ]}
          rows={rows}
        />
      </div>
      <StatusBar panes={[logging ? "Logging" : "Stopped", { text: `${samples.length} samples`, width: 92 }, { text: "bench95_log.csv", width: 118 }]} />
    </Window>
  );
}
Object.assign(window, { LogWindow });
