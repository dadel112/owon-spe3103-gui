"""Der Live-Plot. Spannung auf der linken Achse, Strom auf der rechten,
gemeinsame Zeitachse - pyqtgraph braucht dafuer zwei verkoppelte ViewBoxen."""

from __future__ import annotations

from collections import deque

import pyqtgraph as pg
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QCheckBox, QComboBox, QDoubleSpinBox, QHBoxLayout,
                             QLabel, QPushButton, QVBoxLayout, QWidget)

WINDOWS = [("10 s", 10), ("60 s", 60), ("5 min", 300), ("30 min", 1800)]
MAX_POINTS = 20000          # Notbremse falls beim Trimmen mal etwas schiefgeht


class LivePlot(QWidget):
    """Mitlaufender Plot mit Schwellenlinien und Markern fuer Ausloesungen."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._t = deque(maxlen=MAX_POINTS)
        self._v = deque(maxlen=MAX_POINTS)
        self._i = deque(maxlen=MAX_POINTS)
        self._trips = deque(maxlen=200)
        self._t0 = None
        self._paused = False
        self._window = 60

        pg.setConfigOptions(antialias=False)
        self._plot = pg.PlotWidget()
        self._plot.setBackground("#101418")
        self._plot.showGrid(x=True, y=True, alpha=0.25)
        self._plot.setLabel("left", "Spannung", units="V", color="#38bdf8")
        self._plot.setLabel("bottom", "Zeit", units="s")
        self._plot.setMenuEnabled(False)

        self._vb2 = pg.ViewBox()
        self._plot.plotItem.showAxis("right")
        self._plot.plotItem.scene().addItem(self._vb2)
        self._plot.plotItem.getAxis("right").linkToView(self._vb2)
        self._vb2.setXLink(self._plot.plotItem)
        self._plot.plotItem.getAxis("right").setLabel("Strom", units="A", color="#f59e0b")
        self._plot.plotItem.vb.sigResized.connect(self._sync_views)

        self._curve_v = self._plot.plot(pen=pg.mkPen("#38bdf8", width=2))
        self._curve_i = pg.PlotCurveItem(pen=pg.mkPen("#f59e0b", width=2))
        self._vb2.addItem(self._curve_i)

        dash = Qt.PenStyle.DashLine
        self._ovp_line = pg.InfiniteLine(angle=0, pen=pg.mkPen("#38bdf8", style=dash))
        self._ocp_line = pg.InfiniteLine(angle=0, pen=pg.mkPen("#f59e0b", style=dash))
        self._plot.addItem(self._ovp_line)
        self._vb2.addItem(self._ocp_line)
        self._ovp_line.hide()
        self._ocp_line.hide()
        self._trip_marks = pg.ScatterPlotItem(size=11, symbol="x",
                                              pen=pg.mkPen("#ef4444", width=2),
                                              brush=pg.mkBrush("#ef4444"))
        self._plot.addItem(self._trip_marks)

        self._win_box = QComboBox()
        for label, _ in WINDOWS:
            self._win_box.addItem(label)
        self._win_box.setCurrentIndex(1)
        self._win_box.currentIndexChanged.connect(self._on_window)

        self._auto = QCheckBox("Autoscale")
        self._auto.setChecked(True)
        self._auto.toggled.connect(self._apply_scale)
        self._vmax = QDoubleSpinBox()
        self._vmax.setRange(0.1, 40.0)
        self._vmax.setValue(32.0)
        self._vmax.setSuffix(" V")
        self._vmax.valueChanged.connect(self._apply_scale)
        self._imax = QDoubleSpinBox()
        self._imax.setRange(0.01, 12.0)
        self._imax.setValue(11.0)
        self._imax.setSuffix(" A")
        self._imax.valueChanged.connect(self._apply_scale)

        self._pause_btn = QPushButton("Pause")
        self._pause_btn.setCheckable(True)
        self._pause_btn.toggled.connect(self._on_pause)
        self._clear_btn = QPushButton("Clear")
        self._clear_btn.clicked.connect(self.clear)

        bar = QHBoxLayout()
        bar.addWidget(QLabel("Fenster:"))
        bar.addWidget(self._win_box)
        bar.addWidget(self._auto)
        bar.addWidget(QLabel("Y-max V:"))
        bar.addWidget(self._vmax)
        bar.addWidget(QLabel("Y-max A:"))
        bar.addWidget(self._imax)
        bar.addStretch(1)
        bar.addWidget(self._pause_btn)
        bar.addWidget(self._clear_btn)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self._plot, 1)
        lay.addLayout(bar)
        self._apply_scale()

    # -- Intern -------------------------------------------------------
    def _sync_views(self) -> None:
        self._vb2.setGeometry(self._plot.plotItem.vb.sceneBoundingRect())
        self._vb2.linkedViewChanged(self._plot.plotItem.vb, self._vb2.XAxis)

    def _on_window(self, idx: int) -> None:
        self._window = WINDOWS[idx][1]
        self._redraw()

    def _on_pause(self, on: bool) -> None:
        self._paused = on
        self._pause_btn.setText("Weiter" if on else "Pause")
        if not on:
            self._redraw()

    def _apply_scale(self) -> None:
        auto = self._auto.isChecked()
        self._vmax.setEnabled(not auto)
        self._imax.setEnabled(not auto)
        if auto:
            self._plot.plotItem.vb.enableAutoRange(axis="y")
            self._vb2.enableAutoRange(axis="y")
        else:
            self._plot.plotItem.vb.setYRange(0, self._vmax.value(), padding=0)
            self._vb2.setYRange(0, self._imax.value(), padding=0)

    def _trim(self) -> None:
        """Alles aelter als das Zeitfenster fliegt raus. Laeuft auch waehrend der
        Pause weiter, sonst waechst der Buffer im Hintergrund munter mit."""
        if not self._t:
            return
        cutoff = self._t[-1] - self._window
        while self._t and self._t[0] < cutoff:
            self._t.popleft()
            self._v.popleft()
            self._i.popleft()
        while self._trips and self._trips[0][0] < cutoff:
            self._trips.popleft()

    def _redraw(self) -> None:
        self._trim()
        self._curve_v.setData(list(self._t), list(self._v))
        self._curve_i.setData(list(self._t), list(self._i))
        if self._trips:
            self._trip_marks.setData([p[0] for p in self._trips],
                                     [p[1] for p in self._trips])
        else:
            self._trip_marks.clear()
        if self._t:
            self._plot.setXRange(max(0.0, self._t[-1] - self._window), self._t[-1],
                                 padding=0)
        self._sync_views()

    # -- API ----------------------------------------------------------
    def add_point(self, volt: float, amp: float, ts: float) -> None:
        """Messpunkt anhaengen. Pause haelt nur die Anzeige an, aufgezeichnet
        wird trotzdem weiter."""
        if self._t0 is None:
            self._t0 = ts
        self._t.append(ts - self._t0)
        self._v.append(volt)
        self._i.append(amp)
        if not self._paused:
            self._redraw()
        else:
            self._trim()

    def mark_trip(self, volt: float, ts: float) -> None:
        """Roten Marker am Ausloesezeitpunkt setzen."""
        if self._t0 is None:
            self._t0 = ts
        self._trips.append((ts - self._t0, volt))
        if not self._paused:
            self._redraw()

    def set_thresholds(self, ovp: float | None, ocp: float | None) -> None:
        """Gestrichelte Schwellenlinien setzen (None blendet aus)."""
        for line, value in ((self._ovp_line, ovp), (self._ocp_line, ocp)):
            if value is None:
                line.hide()
            else:
                line.setPos(value)
                line.show()

    def clear(self) -> None:
        """Buffer und Marker leeren."""
        self._t.clear()
        self._v.clear()
        self._i.clear()
        self._trips.clear()
        self._t0 = None
        self._redraw()
