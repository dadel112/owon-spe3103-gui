"""The window. Controls on the left, readings, plot and log on the right.
Nothing here talks to PyVISA directly, everything goes through the driver."""

from __future__ import annotations

import csv
import time

from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDoubleSpinBox,
                             QFileDialog, QFormLayout, QFrame, QGridLayout,
                             QGroupBox, QHBoxLayout, QLabel, QLineEdit,
                             QMainWindow, QMessageBox, QPlainTextEdit,
                             QPushButton, QSlider, QSpinBox, QVBoxLayout, QWidget)

from . import scpi_map
from .driver import DEFAULT_BAUD, DEFAULT_POLL_MS, PsuDriver, list_resources
from .plot import LivePlot

BAUDS = [9600, 19200, 38400, 57600, 115200]
CONFIRM_VOLT = 12.0


class MainWindow(QMainWindow):
    """Main window."""

    def __init__(self, demo: bool = False):
        super().__init__()
        self.demo = demo
        self.setWindowTitle("OWON SPE3103" + (" - DEMO" if demo else ""))
        self.resize(1180, 820)

        self.driver = PsuDriver(demo=demo)
        self._csv_file = None
        self._csv_writer = None
        self._output_on = False
        self._latched = False       # trip waiting to be acknowledged
        self._connected = False
        self._applied: tuple | None = None   # protection values the driver runs on

        self._build_ui()
        self._connect_signals()
        self.driver.start()
        self._refresh_resources()
        self._update_protection_status()
        self._set_connected(False)

    # -- Building the UI ------------------------------------------------
    def _build_ui(self) -> None:
        central = QWidget()
        root = QHBoxLayout(central)
        left = QVBoxLayout()
        right = QVBoxLayout()
        root.addLayout(left, 0)
        root.addLayout(right, 1)
        self.setCentralWidget(central)

        left.addWidget(self._build_connection())
        left.addWidget(self._build_setpoints())
        left.addWidget(self._build_protection())
        left.addWidget(self._build_output())
        left.addStretch(1)

        right.addWidget(self._build_readout())
        self.plot = LivePlot()
        right.addWidget(self.plot, 1)
        right.addWidget(self._build_misc())
        right.addWidget(self._build_log(), 1)

    def _build_connection(self) -> QGroupBox:
        box = QGroupBox("Connection")
        lay = QGridLayout(box)
        self.res_box = QComboBox()
        self.res_box.setEditable(True)
        self.res_box.setMinimumWidth(230)
        self.refresh_btn = QPushButton("Refresh")
        self.baud_box = QComboBox()
        for b in BAUDS:
            self.baud_box.addItem(str(b))
        self.baud_box.setCurrentText(str(DEFAULT_BAUD))
        self.connect_btn = QPushButton("Connect")
        self.disconnect_btn = QPushButton("Disconnect")
        self.status_dot = QLabel("● disconnected")
        self.idn_label = QLabel("IDN: -")
        self.idn_label.setWordWrap(True)

        lay.addWidget(QLabel("Resource:"), 0, 0)
        lay.addWidget(self.res_box, 0, 1)
        lay.addWidget(self.refresh_btn, 0, 2)
        lay.addWidget(QLabel("Baud rate:"), 1, 0)
        lay.addWidget(self.baud_box, 1, 1)
        lay.addWidget(self.connect_btn, 2, 1)
        lay.addWidget(self.disconnect_btn, 2, 2)
        lay.addWidget(self.status_dot, 3, 0, 1, 3)
        lay.addWidget(self.idn_label, 4, 0, 1, 3)
        return box

    def _build_setpoints(self) -> QGroupBox:
        box = QGroupBox("Setpoints")
        lay = QGridLayout(box)
        self.v_spin = QDoubleSpinBox()
        self.v_spin.setRange(0.0, scpi_map.V_MAX)
        self.v_spin.setDecimals(3)
        self.v_spin.setSingleStep(0.1)
        self.v_spin.setSuffix(" V")
        self.v_slider = QSlider(Qt.Orientation.Horizontal)
        self.v_slider.setRange(0, int(scpi_map.V_MAX * 1000))
        self.i_spin = QDoubleSpinBox()
        self.i_spin.setRange(0.0, scpi_map.I_MAX)
        self.i_spin.setDecimals(3)
        self.i_spin.setSingleStep(0.05)
        self.i_spin.setSuffix(" A")
        self.i_slider = QSlider(Qt.Orientation.Horizontal)
        self.i_slider.setRange(0, int(scpi_map.I_MAX * 1000))
        self.apply_btn = QPushButton("Apply")
        self.live_check = QCheckBox("Apply live (on slider release)")

        lay.addWidget(QLabel("Voltage:"), 0, 0)
        lay.addWidget(self.v_spin, 0, 1)
        lay.addWidget(self.v_slider, 1, 0, 1, 2)
        lay.addWidget(QLabel("Current:"), 2, 0)
        lay.addWidget(self.i_spin, 2, 1)
        lay.addWidget(self.i_slider, 3, 0, 1, 2)
        lay.addWidget(self.live_check, 4, 0, 1, 2)
        lay.addWidget(self.apply_btn, 5, 0, 1, 2)
        return box

    def _build_protection(self) -> QGroupBox:
        box = QGroupBox("Protection (OVP / OCP)")
        lay = QFormLayout(box)
        self.ovp_spin = QDoubleSpinBox()
        self.ovp_spin.setRange(0.0, scpi_map.OVP_MAX)
        self.ovp_spin.setDecimals(2)
        # Default to the nameplate rating, not to the clamp maximum: 33 V is
        # above what the supply can put out, so protection armed at that value
        # would never fire.
        self.ovp_spin.setValue(scpi_map.V_MAX)
        self.ovp_spin.setSuffix(" V")
        self.ovp_check = QCheckBox("OVP armed")
        self.ocp_spin = QDoubleSpinBox()
        self.ocp_spin.setRange(0.0, scpi_map.OCP_MAX)
        self.ocp_spin.setDecimals(2)
        self.ocp_spin.setValue(scpi_map.I_MAX)
        self.ocp_spin.setSuffix(" A")
        self.ocp_check = QCheckBox("OCP armed")
        self.delay_spin = QSpinBox()
        self.delay_spin.setRange(0, 2000)
        self.delay_spin.setSuffix(" ms")
        self.prot_apply_btn = QPushButton("Apply protection")
        self.prot_clear_btn = QPushButton("Reset protection")
        self.prot_status = QLabel("-")
        self.prot_status.setWordWrap(True)
        self.prot_hint = QLabel("The software watchdog is limited by the poll interval and is "
                                "no replacement for a fuse or real hardware protection.")
        self.prot_hint.setWordWrap(True)
        self.prot_hint.setStyleSheet("color:#94a3b8; font-size:11px;")
        self.alarm = QLabel("")
        self.alarm.setVisible(False)
        self.alarm.setStyleSheet(
            "background:#7f1d1d; color:white; font-weight:bold; padding:6px;")
        self.alarm.setWordWrap(True)

        lay.addRow("OVP threshold:", self.ovp_spin)
        lay.addRow("", self.ovp_check)
        lay.addRow("OCP threshold:", self.ocp_spin)
        lay.addRow("", self.ocp_check)
        lay.addRow("Trip delay:", self.delay_spin)
        lay.addRow(self.prot_apply_btn)
        lay.addRow(self.prot_clear_btn)
        lay.addRow(self.prot_status)
        lay.addRow(self.prot_hint)
        lay.addRow(self.alarm)
        return box

    def _build_output(self) -> QGroupBox:
        box = QGroupBox("Output")
        lay = QVBoxLayout(box)
        self.output_btn = QPushButton("OUTPUT OFF")
        self.output_btn.setCheckable(True)
        self.output_btn.setMinimumHeight(64)
        self.output_btn.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        lay.addWidget(self.output_btn)
        if self.demo:
            row = QHBoxLayout()
            self.demo_ovp_btn = QPushButton("Demo: force OVP")
            self.demo_ocp_btn = QPushButton("Demo: force OCP")
            row.addWidget(self.demo_ovp_btn)
            row.addWidget(self.demo_ocp_btn)
            lay.addLayout(row)
        self._style_output(False)
        return box

    def _build_readout(self) -> QFrame:
        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.StyledPanel)
        lay = QHBoxLayout(frame)
        font = QFont("Consolas", 40, QFont.Weight.Bold)
        self.v_label = QLabel("0.000 V")
        self.i_label = QLabel("0.000 A")
        self.p_label = QLabel("0.000 W")
        for lbl, color in ((self.v_label, "#38bdf8"), (self.i_label, "#f59e0b"),
                           (self.p_label, "#a3e635")):
            lbl.setFont(font)
            lbl.setStyleSheet(f"color:{color};")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lay.addWidget(lbl, 1)
        self.mode_label = QLabel("--")
        self.mode_label.setFont(QFont("Consolas", 20, QFont.Weight.Bold))
        self.mode_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(self.mode_label, 0)
        return frame

    def _build_misc(self) -> QGroupBox:
        box = QGroupBox("Misc")
        lay = QGridLayout(box)
        self.poll_spin = QSpinBox()
        self.poll_spin.setRange(100, 2000)
        self.poll_spin.setSingleStep(50)
        self.poll_spin.setValue(DEFAULT_POLL_MS)
        self.poll_spin.setSuffix(" ms")
        self.remote_btn = QPushButton("Remote")
        self.local_btn = QPushButton("Local")
        self.raw_edit = QLineEdit()
        self.raw_edit.setPlaceholderText("Raw-SCPI ...")
        self.raw_send_btn = QPushButton("Send")
        self.raw_query_btn = QPushButton("Query")
        self.csv_btn = QPushButton("Record CSV")
        self.csv_btn.setCheckable(True)

        lay.addWidget(QLabel("Polling:"), 0, 0)
        lay.addWidget(self.poll_spin, 0, 1)
        lay.addWidget(self.remote_btn, 0, 2)
        lay.addWidget(self.local_btn, 0, 3)
        lay.addWidget(self.raw_edit, 1, 0, 1, 2)
        lay.addWidget(self.raw_send_btn, 1, 2)
        lay.addWidget(self.raw_query_btn, 1, 3)
        lay.addWidget(self.csv_btn, 2, 0, 1, 4)
        return box

    def _build_log(self) -> QGroupBox:
        box = QGroupBox("Log")
        lay = QVBoxLayout(box)
        self.log_view = QPlainTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setMaximumBlockCount(3000)
        self.log_view.setFont(QFont("Consolas", 9))
        lay.addWidget(self.log_view)
        return box

    # -- Signals ---------------------------------------------------------
    def _connect_signals(self) -> None:
        d = self.driver
        d.reading_ready.connect(self._on_reading)
        d.connection_changed.connect(self._set_connected)
        d.protection_tripped.connect(self._on_trip)
        d.log_message.connect(self._on_log)
        d.error_occurred.connect(lambda t: self._on_log("ERROR", t))
        d.profile_ready.connect(self._on_profile)
        d.idn_ready.connect(lambda s: self.idn_label.setText(f"IDN: {s or 'unknown'}"))
        d.raw_response.connect(lambda s: self.raw_edit.setToolTip(s))
        d.mode_changed.connect(self.mode_label.setText)
        d.setpoints_read.connect(self._on_setpoints)
        d.output_blocked.connect(self._on_output_blocked)

        self.refresh_btn.clicked.connect(self._refresh_resources)
        self.connect_btn.clicked.connect(self._do_connect)
        self.disconnect_btn.clicked.connect(d.request_disconnect)
        self.apply_btn.clicked.connect(self._apply_setpoints)
        self.prot_apply_btn.clicked.connect(self._apply_protection)
        self.prot_clear_btn.clicked.connect(self._clear_protection)
        self.output_btn.toggled.connect(self._on_output_toggle)
        self.poll_spin.valueChanged.connect(d.set_poll_interval)
        self.remote_btn.clicked.connect(lambda: d.send("remote"))
        self.local_btn.clicked.connect(lambda: d.send("local"))
        self.raw_send_btn.clicked.connect(lambda: d.send_raw(self.raw_edit.text(), False))
        self.raw_query_btn.clicked.connect(lambda: d.send_raw(self.raw_edit.text(), True))
        self.csv_btn.toggled.connect(self._on_csv_toggle)
        self.delay_spin.valueChanged.connect(d.protection.set_delay)
        # Thresholds and arming only take effect on 'Apply protection'. Say so
        # instead of letting the panel imply a protection that is not armed yet.
        for signal in (self.ovp_spin.valueChanged, self.ocp_spin.valueChanged,
                       self.ovp_check.toggled, self.ocp_check.toggled):
            signal.connect(lambda *_: self._refresh_protection_dirty())

        self.v_spin.valueChanged.connect(
            lambda v: self.v_slider.setValue(int(round(v * 1000))))
        self.v_slider.valueChanged.connect(lambda x: self.v_spin.setValue(x / 1000.0))
        self.i_spin.valueChanged.connect(
            lambda v: self.i_slider.setValue(int(round(v * 1000))))
        self.i_slider.valueChanged.connect(lambda x: self.i_spin.setValue(x / 1000.0))
        self.v_slider.sliderReleased.connect(self._on_slider_released)
        self.i_slider.sliderReleased.connect(self._on_slider_released)

        if self.demo:
            self.demo_ovp_btn.clicked.connect(lambda: self._force_demo("ovp"))
            self.demo_ocp_btn.clicked.connect(lambda: self._force_demo("ocp"))

    # -- Actions ---------------------------------------------------------
    def _refresh_resources(self) -> None:
        current = self.res_box.currentText()
        self.res_box.clear()
        if self.demo:
            self.res_box.addItem("DEMO")
        else:
            self.res_box.addItems(list_resources())
        if current:
            self.res_box.setEditText(current)

    def _do_connect(self) -> None:
        self.driver.request_connect(self.res_box.currentText().strip(),
                                    int(self.baud_box.currentText()))

    def _apply_setpoints(self) -> None:
        self.driver.apply_voltage(self.v_spin.value())
        self.driver.apply_current(self.i_spin.value())

    def _on_slider_released(self) -> None:
        if self.live_check.isChecked():
            self._apply_setpoints()

    def _apply_protection(self) -> None:
        self.driver.protection.set_delay(self.delay_spin.value())
        self.driver.apply_ovp(self.ovp_spin.value(), self.ovp_check.isChecked())
        self.driver.apply_ocp(self.ocp_spin.value(), self.ocp_check.isChecked())
        self.plot.set_thresholds(
            self.ovp_spin.value() if self.ovp_check.isChecked() else None,
            self.ocp_spin.value() if self.ocp_check.isChecked() else None)
        self._applied = self._protection_fields()
        self._refresh_protection_dirty()
        self.driver.warn_unreachable_protection()
        self._update_protection_status()

    def _protection_fields(self) -> tuple:
        return (round(self.ovp_spin.value(), 2), self.ovp_check.isChecked(),
                round(self.ocp_spin.value(), 2), self.ocp_check.isChecked())

    def _refresh_protection_dirty(self) -> None:
        """Highlight 'Apply protection' while the fields differ from what the
        watchdog actually runs on - a ticked box on its own protects nothing."""
        if self._applied is None:
            dirty = self.ovp_check.isChecked() or self.ocp_check.isChecked()
        else:
            dirty = self._applied != self._protection_fields()
        self.prot_apply_btn.setText(
            "Apply protection (pending)" if dirty else "Apply protection")
        self.prot_apply_btn.setStyleSheet(
            "font-weight:bold; background:#b45309; color:white;" if dirty else "")

    def _clear_protection(self) -> None:
        self.driver.clear_protection()
        self._latched = False
        self.alarm.setVisible(False)
        self.output_btn.setEnabled(self._connected)
        self._update_protection_status()

    def _update_protection_status(self) -> None:
        self.prot_status.setText(self.driver.protection.stage_text())

    def _on_output_toggle(self, on: bool) -> None:
        if on and self._latched:
            QMessageBox.warning(self, "Protection tripped",
                                "A trip is still latched. Clear it with "
                                "'Reset protection' before switching on again.")
            self.output_btn.setChecked(False)
            return
        if on and self.v_spin.value() > CONFIRM_VOLT:
            answer = QMessageBox.question(
                self, "Switch output on",
                f"Setpoint is {self.v_spin.value():.2f} V, above the "
                f"{CONFIRM_VOLT:.0f} V mark. Switch on anyway?")
            if answer != QMessageBox.StandardButton.Yes:
                self.output_btn.setChecked(False)
                return
        self._output_on = on
        self._style_output(on)
        self.driver.send("output_on" if on else "output_off")

    def _style_output(self, on: bool) -> None:
        self.output_btn.setText("OUTPUT ON" if on else "OUTPUT OFF")
        self.output_btn.setStyleSheet(
            "background:#16a34a; color:white;" if on else "background:#475569; color:#e2e8f0;")

    def _force_demo(self, kind: str) -> None:
        dev = self.driver.demo_device
        if dev is None:
            self._on_log("WARN", "demo device not connected")
            return
        if kind == "ovp":
            dev.force_ovp = True
        else:
            dev.force_ocp = True
        self._on_log("INFO", f"demo: forcing {kind.upper()} trip")

    def _on_csv_toggle(self, on: bool) -> None:
        if on:
            path, _ = QFileDialog.getSaveFileName(self, "Save CSV", "psu_log.csv",
                                                  "CSV (*.csv)")
            if not path:
                self.csv_btn.setChecked(False)
                return
            self._csv_file = open(path, "w", newline="", encoding="utf-8")
            self._csv_writer = csv.writer(self._csv_file)
            self._csv_writer.writerow(["timestamp", "volt", "ampere", "watt"])
            self.csv_btn.setText("Stop recording")
        else:
            self._close_csv()
            self.csv_btn.setText("Record CSV")

    def _close_csv(self) -> None:
        if self._csv_file:
            self._csv_file.close()
        self._csv_file = None
        self._csv_writer = None

    # -- Slots -----------------------------------------------------------
    @pyqtSlot(float, float, float, float)
    def _on_reading(self, v: float, i: float, p: float, ts: float) -> None:
        self.v_label.setText(f"{v:6.3f} V")
        self.i_label.setText(f"{i:6.3f} A")
        self.p_label.setText(f"{p:6.3f} W")
        self.plot.add_point(v, i, ts)
        if self._csv_writer:
            self._csv_writer.writerow([f"{ts:.3f}", f"{v:.4f}", f"{i:.4f}", f"{p:.4f}"])

    @pyqtSlot(bool)
    def _set_connected(self, ok: bool) -> None:
        self.status_dot.setText("● connected" if ok else "● disconnected")
        self.status_dot.setStyleSheet(f"color:{'#16a34a' if ok else '#94a3b8'};")
        self.connect_btn.setEnabled(not ok)
        self.disconnect_btn.setEnabled(ok)
        self._connected = ok
        for w in (self.apply_btn, self.output_btn, self.prot_apply_btn,
                  self.prot_clear_btn, self.raw_send_btn, self.raw_query_btn):
            w.setEnabled(ok)
        if ok:
            # The driver clears a leftover trip when it connects.
            self._latched = False
            self.alarm.setVisible(False)
            # Nothing is armed on a fresh connection, whatever the fields show.
            self._applied = None
            self._refresh_protection_dirty()
            self._update_protection_status()
        if not ok:
            self.output_btn.blockSignals(True)
            self.output_btn.setChecked(False)
            self.output_btn.blockSignals(False)
            self._style_output(False)
            self.mode_label.setText("--")

    @pyqtSlot(dict)
    def _on_profile(self, profile: dict) -> None:
        """Grey out and label whatever discovery could not resolve. A visibly dead
        control beats a button that silently does nothing.
        """
        def mark(widget, key: str, label: str) -> None:
            ok = bool(profile.get(key))
            widget.setEnabled(ok)
            if not ok:
                widget.setToolTip(f"{label} not supported by this device")
                if isinstance(widget, (QCheckBox, QPushButton)):
                    widget.setText(widget.text() + " (not supported)")

        mark(self.ovp_check, "ovp_set", "Hardware-OVP")
        mark(self.ocp_check, "ocp_set", "Hardware-OCP")
        mark(self.prot_clear_btn, "prot_clear", "Protection reset")
        mark(self.remote_btn, "remote", "Remote")
        mark(self.local_btn, "local", "Local")
        # The checkboxes stay usable either way, without device-side protection
        # only the software watchdog applies.
        self.ovp_check.setEnabled(True)
        self.ocp_check.setEnabled(True)
        missing = sorted(k for k, v in profile.items() if not v)
        if missing:
            self._on_log("WARN", "not supported: " + ", ".join(missing))
        self._update_protection_status()

    @pyqtSlot(float, float)
    def _on_setpoints(self, v: float, i: float) -> None:
        self.v_spin.setValue(min(v, scpi_map.V_MAX))
        self.i_spin.setValue(min(i, scpi_map.I_MAX))

    @pyqtSlot(str, float)
    def _on_trip(self, kind: str, value: float) -> None:
        unit = "V" if kind == "OVP" else "A"
        stamp = time.strftime("%H:%M:%S")
        self.alarm.setText(f"{stamp}  {kind} TRIPPED at {value:.3f} {unit} - "
                           f"output switched off. Clear it with 'Reset protection'.")
        self.alarm.setVisible(True)
        QApplication.beep()
        self._latched = True
        self._output_on = False
        self.output_btn.blockSignals(True)
        self.output_btn.setChecked(False)
        self.output_btn.blockSignals(False)
        self._style_output(False)
        # The watchdog does not evaluate anything while latched, so the output
        # stays locked until the trip is acknowledged.
        self.output_btn.setEnabled(False)
        self._update_protection_status()
        self.plot.mark_trip(value, time.time())

    @pyqtSlot(str)
    def _on_output_blocked(self, reason: str) -> None:
        """The driver refused to switch the output on."""
        self._latched = True
        self.output_btn.blockSignals(True)
        self.output_btn.setChecked(False)
        self.output_btn.blockSignals(False)
        self._style_output(False)
        self.output_btn.setEnabled(False)
        self._on_log("WARN", reason)

    @pyqtSlot(str, str)
    def _on_log(self, level: str, text: str) -> None:
        self.log_view.appendPlainText(f"{time.strftime('%H:%M:%S')} [{level}] {text}")

    # -- Shutdown --------------------------------------------------------
    def closeEvent(self, event) -> None:
        self._close_csv()
        self.driver.stop()
        self.driver.wait(4000)
        super().closeEvent(event)
