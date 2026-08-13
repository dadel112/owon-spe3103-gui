/* Device connection dialog — the first thing the program shows. */
function ConnectDialog({ ds, state, dispatch }) {
  const { Window, Panel, Button, Select, TextField, Checkbox, Icon } = ds;
  const [port, setPort] = React.useState(state.port);
  const [baud, setBaud] = React.useState("9600");
  const [driver, setDriver] = React.useState("scpi-generic");
  const [probe, setProbe] = React.useState(true);
  return (
    <Window title="Connect to device" icon="power" width={368} buttons={["close"]} onButton={() => dispatch({ type: "closeConnect" })} style={{ boxShadow: "var(--bevel-out), var(--shadow-hard)", background: "var(--surface-dialog)" }}>
      <div style={{ padding: "var(--space-11)", display: "flex", flexDirection: "column", gap: "var(--space-8)" }}>
        <div style={{ display: "grid", gridTemplateColumns: "auto 1fr", gap: "var(--space-6) var(--space-8)", alignItems: "center" }}>
          <span>Serial port</span>
          <Select value={port} options={["COM1", "COM3", "COM4", "/dev/ttyUSB0"]} onChange={setPort} width={190} />
          <span>Baud rate</span>
          <Select value={baud} options={["9600", "19200", "38400", "115200"]} onChange={setBaud} width={110} />
          <span>Driver</span>
          <Select value={driver} options={[{ value: "scpi-generic", label: "SCPI (generic)" }, { value: "psu3005", label: "PSU-3005 series" }, { value: "modbus", label: "Modbus RTU" }]} onChange={setDriver} width={190} />
          <span>Timeout</span>
          <TextField value="1.5" mono align="right" width={64} />
        </div>
        <Panel label="On connect" bodyStyle={{ display: "flex", flexDirection: "column", gap: "var(--space-4)" }}>
          <Checkbox checked={probe} onChange={setProbe} label="Query *IDN? and verify model" />
          <Checkbox checked label="Read setpoints from device" />
          <Checkbox checked={false} label="Enable output immediately" />
        </Panel>
        <div style={{ display: "flex", alignItems: "center", gap: "var(--space-8)", font: "var(--type-label)", color: "var(--grey-700)" }}>
          <Icon name="info-box" size={16} />
          <span>python -m bench95 --port {port} --baud {baud}</span>
        </div>
        <div style={{ display: "flex", justifyContent: "flex-end", gap: "var(--space-8)" }}>
          <Button isDefault onClick={() => dispatch({ type: "connect", port })}>Connect</Button>
          <Button onClick={() => dispatch({ type: "closeConnect" })}>Cancel</Button>
        </div>
      </div>
    </Window>
  );
}
Object.assign(window, { ConnectDialog });
