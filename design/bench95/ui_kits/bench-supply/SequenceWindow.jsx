/* Sequence editor — the step list a Python script would run against the supply. */
function SequenceWindow({ ds, state, dispatch }) {
  const { Window, Toolbar, ToolbarGrip, ToolbarSeparator, IconButton, ListView, Panel, Button, NumberSpinner, Checkbox, ProgressBar, StatusBar, Tooltip } = ds;
  const { steps, seqIndex, seqRunning, seqProgress } = state;
  const [sel, setSel] = React.useState(0);
  const rows = steps.map((s, i) => ({
    n: String(i + 1).padStart(2, "0"),
    v: s.v.toFixed(3),
    i: s.i.toFixed(3),
    d: s.dwell.toFixed(1) + " s",
    note: s.note,
    run: seqRunning && i === seqIndex ? "▶" : "",
  }));
  return (
    <Window title="Sequence — ramp_test.b95" icon="sliders" width={468} onButton={(b) => dispatch({ type: "windowButton", target: "sequence", button: b })}>
      <Toolbar>
        <ToolbarGrip />
        <Tooltip text="Run sequence (F9)"><IconButton icon="play" label="Run" active={seqRunning} onClick={() => dispatch({ type: "runSequence" })} disabled={!state.connected} /></Tooltip>
        <Tooltip text="Hold"><IconButton icon="pause" label="Hold" disabled={!seqRunning} /></Tooltip>
        <ToolbarSeparator />
        <Tooltip text="Add step"><IconButton icon="plus" label="Add step" /></Tooltip>
        <Tooltip text="Remove step"><IconButton icon="minus" label="Remove step" /></Tooltip>
        <Tooltip text="Move up"><IconButton icon="arrow-up" label="Move up" /></Tooltip>
        <Tooltip text="Move down"><IconButton icon="arrow-down" label="Move down" /></Tooltip>
        <ToolbarSeparator />
        <Tooltip text="Save sequence"><IconButton icon="save" label="Save" /></Tooltip>
      </Toolbar>
      <div style={{ padding: "var(--space-8)", display: "flex", flexDirection: "column", gap: "var(--space-8)" }}>
        <ListView
          mono
          height={148}
          selectedIndex={sel}
          onSelect={setSel}
          columns={[
            { key: "run", label: "", width: 18 },
            { key: "n", label: "#", width: 28 },
            { key: "v", label: "Volts", width: 62, align: "right" },
            { key: "i", label: "Amps", width: 62, align: "right" },
            { key: "d", label: "Dwell", width: 58, align: "right" },
            { key: "note", label: "Comment" },
          ]}
          rows={rows}
        />
        <div style={{ display: "flex", gap: "var(--space-8)", alignItems: "flex-start" }}>
          <Panel label={`Step ${sel + 1}`} style={{ flex: "0 0 auto" }} bodyStyle={{ display: "grid", gridTemplateColumns: "auto auto", gap: "var(--space-4) var(--space-6)", alignItems: "center" }}>
            <span>Volts</span>
            <NumberSpinner value={steps[sel].v} onChange={(v) => dispatch({ type: "editStep", index: sel, key: "v", value: v })} step={0.1} max={30} decimals={3} unit="V" width={92} />
            <span>Amps</span>
            <NumberSpinner value={steps[sel].i} onChange={(v) => dispatch({ type: "editStep", index: sel, key: "i", value: v })} step={0.01} max={5} decimals={3} unit="A" width={92} />
            <span>Dwell</span>
            <NumberSpinner value={steps[sel].dwell} onChange={(v) => dispatch({ type: "editStep", index: sel, key: "dwell", value: v })} step={0.5} max={600} decimals={1} unit="s" width={92} />
          </Panel>
          <Panel label="Run options" style={{ flex: "1 1 auto" }} bodyStyle={{ display: "flex", flexDirection: "column", gap: "var(--space-4)" }}>
            <Checkbox checked label="Log each step to CSV" />
            <Checkbox checked={false} label="Loop sequence" />
            <Checkbox checked label="Disable output when finished" />
            <div style={{ display: "flex", gap: "var(--space-6)", marginTop: "var(--space-4)" }}>
              <Button size="sm" onClick={() => dispatch({ type: "runSequence" })} disabled={!state.connected || seqRunning}>Run</Button>
              <Button size="sm" disabled={!seqRunning} onClick={() => dispatch({ type: "stopSequence" })}>Stop</Button>
            </div>
          </Panel>
        </div>
        <ProgressBar value={seqProgress} label={`${Math.round(seqProgress)}%`} style={{ width: "100%" }} />
      </div>
      <StatusBar panes={[seqRunning ? `Running step ${seqIndex + 1} of ${steps.length}` : "Idle", { text: `${steps.length} steps`, width: 70 }, { text: "ramp_test.b95", width: 106 }]} />
    </Window>
  );
}
Object.assign(window, { SequenceWindow });
