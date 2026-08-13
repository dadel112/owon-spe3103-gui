# Bench95 Supply — UI kit

An interactive recreation of the product: a single-window Python utility that drives a 30 V / 5 A programmable bench supply over serial, running on a period desktop.

Open `index.html`. It boots into the connect dialog, exactly as the program does.

## What you can do

1. **Connect** — pick a port, baud rate and driver, press Connect. The console logs `*IDN?` and the reply.
2. **Set and enable** — type or drag voltage/current setpoints, then hit the big OUTPUT button (or the toolbar bolt). Readouts come alive with a little jitter; watts are derived.
3. **Trip protection** — raise the voltage setpoint above the OVP level (13.50 V by default). OVP latches, the output drops, the red TRIP lamp blinks and the status bar goes red. Clear it from **Device → Clear Trip**.
4. **Run a sequence** — **View → Sequence Editor**, edit a step, press Run. Steps advance, the progress bar fills in chunks, the output disables at the end.
5. **Watch the log** — **View → Data Log**. Live trace (volts green, amps amber), newest-first sample table, CSV export button.
6. **Talk SCPI** — **View → SCPI Console**. `MEAS:VOLT?`, `MEAS:CURR?`, `*IDN?` answer; anything else returns `OK`.
7. **Disconnect with the output on** — refused with a warning dialog.

Task-bar buttons and desktop icons (double-click) raise windows; the active window's task button stays latched.

## Files

| File | Screen |
| --- | --- |
| `index.html` | Page shell: loads the bundle, the screens, mounts `Desktop`. |
| `Desktop.jsx` | Desktop shell, window manager, and the whole app reducer (state + fake instrument). |
| `MainWindow.jsx` | Control window: menu bar, toolbar, measured readouts, setpoints, protection, regulation, status bar. |
| `ConnectDialog.jsx` | Device connection dialog. |
| `SequenceWindow.jsx` | Step list editor with run controls and progress. |
| `LogWindow.jsx` | Live plot, sample table, logging controls. |
| `ScpiConsole.jsx` | Raw command console. |

Every widget comes from the design system's own components — the kit adds layout and fake device behaviour only. Screens are loaded as `text/babel` and publish themselves on `window`; they take `{ ds, state, dispatch }`, where `ds` is the compiled component namespace.

## Known liberties

The device, its model number and its command set are invented (no real program or manual was supplied). Window dragging, resizing, real serial I/O, file dialogs and profile persistence are out of scope — buttons for them are present and inert, which is how a mock-up should read.
