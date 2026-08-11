"""PyQt6-Hauptfenster: Verbindung, Sollwerte, Schutz, Messung, Plot, Log."""

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
    """Hauptfenster der Netzteilsteuerung."""

    def __init__(self, demo: bool = False):
        super().__init__()
        self.demo = demo
        self.setWindowTitle("OWON SPE3103" + (" - DEMO" if demo else ""))
        self.resize(1180, 820)

        self.driver = PsuDriver(demo=demo)
        self._csv_file = None
        self._csv_writer = None
        self._output_on = False

        self._build_ui()
        self._connect_signals()
        self.driver.start()
        self._refresh_resources()
        self._update_protection_status()
        self._set_connected(False)

    # -- UI-Aufbau ----------------------------------------------------
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
        box = QGroupBox("Verbindung")
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
        self.status_dot = QLabel("● getrennt")
        self.idn_label = QLabel("IDN: -")
        self.idn_label.setWordWrap(True)

        lay.addWidget(QLabel("Ressource:"), 0, 0)
        lay.addWidget(self.res_box, 0, 1)
        lay.addWidget(self.refresh_btn, 0, 2)
        lay.addWidget(QLabel("Baudrate:"), 1, 0)
        lay.addWidget(self.baud_box, 1, 1)
        lay.addWidget(self.connect_btn, 2, 1)
        lay.addWidget(self.disconnect_btn, 2, 2)
        lay.addWidget(self.status_dot, 3, 0, 1, 3)
        lay.addWidget(self.idn_label, 4, 0, 1, 3)
        return box

    def _build_setpoints(self) -> QGroupBox:
        box = QGroupBox("Sollwerte")
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
        self.apply_btn = QPushButton("Setzen")
        self.live_check = QCheckBox("Live uebernehmen (beim Loslassen)")

        lay.addWidget(QLabel("Spannung:"), 0, 0)
        lay.addWidget(self.v_spin, 0, 1)
        lay.addWidget(self.v_slider, 1, 0, 1, 2)
        lay.addWidget(QLabel("Strom:"), 2, 0)
        lay.addWidget(self.i_spin, 2, 1)
        lay.addWidget(self.i_slider, 3, 0, 1, 2)
        lay.addWidget(self.live_check, 4, 0, 1, 2)
        lay.addWidget(self.apply_btn, 5, 0, 1, 2)
        return box

    def _build_protection(self) -> QGroupBox:
        box = QGroupBox("Schutz (OVP / OCP)")
        lay = QFormLayout(box)
        self.ovp_spin = QDoubleSpinBox()
        self.ovp_spin.setRange(0.0, scpi_map.OVP_MAX)
        self.ovp_spin.setDecimals(2)
        self.ovp_spin.setValue(scpi_map.OVP_MAX)
        self.ovp_spin.setSuffix(" V")
        self.ovp_check = QCheckBox("OVP aktiv")
        self.ocp_spin = QDoubleSpinBox()
        self.ocp_spin.setRange(0.0, scpi_map.OCP_MAX)
        self.ocp_spin.setDecimals(2)
        self.ocp_spin.setValue(scpi_map.OCP_MAX)
        self.ocp_spin.setSuffix(" A")
        self.ocp_check = QCheckBox("OCP aktiv")
        self.delay_spin = QSpinBox()
        self.delay_spin.setRange(0, 2000)
        self.delay_spin.setSuffix(" ms")
        self.prot_apply_btn = QPushButton("Schutz uebernehmen")
        self.prot_clear_btn = QPushButton("Schutz zuruecksetzen")
        self.prot_status = QLabel("-")
        self.prot_status.setWordWrap(True)
        self.prot_hint = QLabel("Software-Ueberwachung ist durch das Polling-Intervall "
                                "begrenzt und ersetzt keine Hardware-Sicherung.")
        self.prot_hint.setWordWrap(True)
        self.prot_hint.setStyleSheet("color:#94a3b8; font-size:11px;")
        self.alarm = QLabel("")
        self.alarm.setVisible(False)
        self.alarm.setStyleSheet(
            "background:#7f1d1d; color:white; font-weight:bold; padding:6px;")
        self.alarm.setWordWrap(True)

        lay.addRow("OVP-Schwelle:", self.ovp_spin)
        lay.addRow("", self.ovp_check)
        lay.addRow("OCP-Schwelle:", self.ocp_spin)
        lay.addRow("", self.ocp_check)
        lay.addRow("Ansprechverzoegerung:", self.delay_spin)
        lay.addRow(self.prot_apply_btn)
        lay.addRow(self.prot_clear_btn)
        lay.addRow(self.prot_status)
        lay.addRow(self.prot_hint)
        lay.addRow(self.alarm)
        return box

    def _build_output(self) -> QGroupBox:
        box = QGroupBox("Ausgang")
        lay = QVBoxLayout(box)
        self.output_btn = QPushButton("AUSGANG AUS")
        self.output_btn.setCheckable(True)
        self.output_btn.setMinimumHeight(64)
        self.output_btn.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        lay.addWidget(self.output_btn)
        if self.demo:
            row = QHBoxLayout()
            self.demo_ovp_btn = QPushButton("Demo: OVP ausloesen")
            self.demo_ocp_btn = QPushButton("Demo: OCP ausloesen")
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
        box = QGroupBox("Sonstiges")
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
        self.csv_btn = QPushButton("CSV aufzeichnen")
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

    # -- Signale ------------------------------------------------------
    def _connect_signals(self) -> None:
        d = self.driver
        d.reading_ready.connect(self._on_reading)
        d.connection_changed.connect(self._set_connected)
        d.protection_tripped.connect(self._on_trip)
        d.log_message.connect(self._on_log)
        d.error_occurred.connect(lambda t: self._on_log("ERROR", t))
        d.profile_ready.connect(self._on_profile)
        d.idn_ready.connect(lambda s: self.idn_label.setText(f"IDN: {s or 'unbekannt'}"))
        d.raw_response.connect(lambda s: self.raw_edit.setToolTip(s))
        d.mode_changed.connect(self.mode_label.setText)
        d.setpoints_read.connect(self._on_setpoints)

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

    # -- Aktionen -----------------------------------------------------
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
        self._update_protection_status()

    def _clear_protection(self) -> None:
        self.driver.clear_protection()
        self.alarm.setVisible(False)
        self._update_protection_status()

    def _update_protection_status(self) -> None:
        self.prot_status.setText(self.driver.protection.stage_text())

    def _on_output_toggle(self, on: bool) -> None:
        if on and self.v_spin.value() > CONFIRM_VOLT:
            answer = QMessageBox.question(
                self, "Ausgang einschalten",
                f"Sollspannung {self.v_spin.value():.2f} V liegt ueber "
                f"{CONFIRM_VOLT:.0f} V. Wirklich einschalten?")
            if answer != QMessageBox.StandardButton.Yes:
                self.output_btn.setChecked(False)
                return
        self._output_on = on
        self._style_output(on)
        self.driver.send("output_on" if on else "output_off")

    def _style_output(self, on: bool) -> None:
        self.output_btn.setText("AUSGANG AN" if on else "AUSGANG AUS")
        self.output_btn.setStyleSheet(
            "background:#16a34a; color:white;" if on else "background:#475569; color:#e2e8f0;")

    def _force_demo(self, kind: str) -> None:
        dev = self.driver.demo_device
        if dev is None:
            self._on_log("WARN", "Demo-Geraet nicht verbunden")
            return
        if kind == "ovp":
            dev.force_ovp = True
        else:
            dev.force_ocp = True
        self._on_log("INFO", f"Demo: {kind.upper()}-Ausloesung erzwungen")

    def _on_csv_toggle(self, on: bool) -> None:
        if on:
            path, _ = QFileDialog.getSaveFileName(self, "CSV speichern", "psu_log.csv",
                                                  "CSV (*.csv)")
            if not path:
                self.csv_btn.setChecked(False)
                return
            self._csv_file = open(path, "w", newline="", encoding="utf-8")
            self._csv_writer = csv.writer(self._csv_file)
            self._csv_writer.writerow(["timestamp", "volt", "ampere", "watt"])
            self.csv_btn.setText("Aufzeichnung stoppen")
        else:
            self._close_csv()
            self.csv_btn.setText("CSV aufzeichnen")

    def _close_csv(self) -> None:
        if self._csv_file:
            self._csv_file.close()
        self._csv_file = None
        self._csv_writer = None

    # -- Slots --------------------------------------------------------
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
        self.status_dot.setText("● verbunden" if ok else "● getrennt")
        self.status_dot.setStyleSheet(f"color:{'#16a34a' if ok else '#94a3b8'};")
        self.connect_btn.setEnabled(not ok)
        self.disconnect_btn.setEnabled(ok)
        for w in (self.apply_btn, self.output_btn, self.prot_apply_btn,
                  self.prot_clear_btn, self.raw_send_btn, self.raw_query_btn):
            w.setEnabled(ok)
        if not ok:
            self.output_btn.blockSignals(True)
            self.output_btn.setChecked(False)
            self.output_btn.blockSignals(False)
            self._style_output(False)
            self.mode_label.setText("--")

    @pyqtSlot(dict)
    def _on_profile(self, profile: dict) -> None:
        """Nicht aufgeloeste Funktionen sichtbar deaktivieren."""
        def mark(widget, key: str, label: str) -> None:
            ok = bool(profile.get(key))
            widget.setEnabled(ok)
            if not ok:
                widget.setToolTip(f"{label} nicht unterstuetzt")
                if isinstance(widget, (QCheckBox, QPushButton)):
                    widget.setText(widget.text() + " (nicht unterstuetzt)")

        mark(self.ovp_check, "ovp_set", "Hardware-OVP")
        mark(self.ocp_check, "ocp_set", "Hardware-OCP")
        mark(self.prot_clear_btn, "prot_clear", "Schutz-Reset")
        mark(self.remote_btn, "remote", "Remote")
        mark(self.local_btn, "local", "Local")
        self.ovp_check.setEnabled(True)      # Software-OVP bleibt immer moeglich
        self.ocp_check.setEnabled(True)
        missing = sorted(k for k, v in profile.items() if not v)
        if missing:
            self._on_log("WARN", "nicht unterstuetzt: " + ", ".join(missing))
        self._update_protection_status()

    @pyqtSlot(float, float)
    def _on_setpoints(self, v: float, i: float) -> None:
        self.v_spin.setValue(min(v, scpi_map.V_MAX))
        self.i_spin.setValue(min(i, scpi_map.I_MAX))

    @pyqtSlot(str, float)
    def _on_trip(self, kind: str, value: float) -> None:
        unit = "V" if kind == "OVP" else "A"
        stamp = time.strftime("%H:%M:%S")
        self.alarm.setText(f"{stamp}  {kind} AUSGELOEST bei {value:.3f} {unit} - "
                           f"Ausgang abgeschaltet. Reset ueber 'Schutz zuruecksetzen'.")
        self.alarm.setVisible(True)
        QApplication.beep()
        self.output_btn.blockSignals(True)
        self.output_btn.setChecked(False)
        self.output_btn.blockSignals(False)
        self._style_output(False)
        self.plot.mark_trip(value if kind == "OVP" else value, time.time())

    @pyqtSlot(str, str)
    def _on_log(self, level: str, text: str) -> None:
        self.log_view.appendPlainText(f"{time.strftime('%H:%M:%S')} [{level}] {text}")

    # -- Ende ---------------------------------------------------------
    def closeEvent(self, event) -> None:
        self._close_csv()
        self.driver.stop()
        self.driver.wait(4000)
        super().closeEvent(event)
