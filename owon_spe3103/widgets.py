"""Bench95 instrument widgets - the pieces of the design system that Qt has no
equivalent for: the LED readout well, the indicator lamp and the status pane.

Ported from design/bench95/components/display/{LedReadout,Led,StatusBar}.jsx.
"""

from __future__ import annotations

from PyQt6.QtCore import QSize, QTimer, Qt
from PyQt6.QtGui import QColor, QFont, QFontMetrics, QPainter
from PyQt6.QtWidgets import QLabel, QSizePolicy, QWidget

from . import theme

_LED_COLOURS = {
    "green": (theme.LED_GREEN, theme.LED_GREEN_DIM, theme.READOUT_BG),
    "amber": (theme.LED_AMBER, theme.LED_AMBER_DIM, theme.READOUT_BG_AMBER),
    "red": (theme.LED_RED, theme.LED_RED_DIM, theme.READOUT_BG),
}

def _readout_size(name: str) -> int:
    """The digit height for a well size. Looked up rather than tabulated: the
    tokens are restated for the display when the theme is applied, and this
    module is imported long before that happens."""
    return {"sm": theme.TEXT_READOUT_SM, "md": theme.TEXT_READOUT_MD,
            "lg": theme.TEXT_READOUT_LG}[name]


def _paint_bevel(painter: QPainter, w: int, h: int, layers) -> None:
    """Draw one of the token bevels onto an arbitrary rectangle."""
    for thickness, side, colour in layers:
        c = QColor(colour)
        if side == "tl":
            painter.fillRect(0, 0, w, thickness, c)
            painter.fillRect(0, 0, thickness, h, c)
        else:
            painter.fillRect(0, h - thickness, w, thickness, c)
            painter.fillRect(w - thickness, 0, thickness, h, c)


def _scanlines(painter: QPainter, w: int, h: int) -> None:
    """1-in-3 scanlines over the well, inset past the bevel."""
    line, inset = theme.px(1), theme.px(2)
    for y in range(theme.px(4), h - inset, theme.px(3)):
        painter.fillRect(inset, y, w - 2 * inset, line, theme.CRT_LINE)


class LedReadout(QWidget):
    """A sunken LED well: pixel caption, glowing digits, unit slot, scanlines.

    `off` dims the digits to the unlit segment colour instead of hiding them -
    a dark readout still shows the instrument is there, just not driving.
    """

    def __init__(self, label: str, unit: str = "", digits: int = 3,
                 colour: str = "green", size: str = "md", parent=None):
        super().__init__(parent)
        self._label = label
        self._unit = unit
        self._digits = digits
        self._colour = colour
        self._size = size
        self._value = 0.0
        self._off = True
        # Preferred vertically, so wells of different digit sizes sitting in one
        # row all take the row's height instead of leaving a ragged top edge.
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self._digit_font = theme.mono_font(_readout_size(size))
        self._unit_font = theme.mono_font(theme.TEXT_READOUT_SM)
        self._caption_font = theme.pixel_font(theme.TEXT_2XS)

    # -- API -----------------------------------------------------------
    def set_value(self, value: float) -> None:
        self._value = value
        self.update()

    def set_off(self, off: bool) -> None:
        """Unlit means the output is off; the numbers stay, dimmed."""
        if off != self._off:
            self._off = off
            self.update()

    def value(self) -> float:
        return self._value

    # -- Painting --------------------------------------------------------
    def _text(self) -> str:
        return f"{self._value:.{self._digits}f}"

    def _padding(self) -> tuple[int, int]:
        """The well's inner inset, horizontal and vertical."""
        return theme.SPACE_8, theme.SPACE_4 + theme.BEVEL

    def _fitted_font(self, width: int, height: int) -> QFont:
        """The digits at the largest size that still fits the well.

        The wells are laid out, not placed at fixed coordinates, so a narrow
        window makes them narrow. Shrinking the type keeps the reading whole;
        drawing it at the token size would run it past the bevel.
        """
        font = QFont(self._digit_font)
        floor = theme.TEXT_READOUT_SM // 2
        while font.pixelSize() > floor:
            fm = QFontMetrics(font)
            if fm.horizontalAdvance(self._text()) <= width and fm.height() <= height:
                break
            font.setPixelSize(font.pixelSize() - 1)
        return font

    def sizeHint(self):
        fm = QFontMetrics(self._digit_font)
        cap = QFontMetrics(self._caption_font).height() if self._label else 0
        _, pad_y = self._padding()
        width = fm.horizontalAdvance("0" * (self._digits + 3)) + theme.px(60)
        return QSize(width, fm.height() + cap + 2 * pad_y + 2 * theme.SPACE_4)

    def minimumSizeHint(self):
        """Deliberately well under sizeHint: a cramped window should narrow the
        wells, not refuse to shrink and push the panel off the screen."""
        fm = QFontMetrics(theme.mono_font(theme.TEXT_READOUT_SM))
        cap = QFontMetrics(self._caption_font).height() if self._label else 0
        pad_x, pad_y = self._padding()
        width = fm.horizontalAdvance("0" * (self._digits + 2)) + 2 * pad_x
        return QSize(width, fm.height() + cap + 2 * pad_y)

    def paintEvent(self, event) -> None:
        lit, dim, background = _LED_COLOURS[self._colour]
        fg = QColor(dim if self._off else lit)
        w, h = self.width(), self.height()
        pad_x, pad_y = self._padding()

        p = QPainter(self)
        p.fillRect(0, 0, w, h, QColor(background))
        _paint_bevel(p, w, h, theme.bevel_layers("in"))

        top = pad_y
        if self._label:
            p.setFont(self._caption_font)
            caption = QColor(fg)
            caption.setAlphaF(0.65)
            p.setPen(caption)
            fm = p.fontMetrics()
            p.drawText(pad_x, top + fm.ascent(), self._label)
            top += fm.height() + theme.px(2)

        right = w - pad_x
        unit_width = 0
        if self._unit:
            ufm = QFontMetrics(self._unit_font)
            unit_width = ufm.horizontalAdvance(self._unit) + theme.SPACE_6

        digit_font = self._fitted_font(w - 2 * pad_x - unit_width, h - top - pad_y)
        p.setFont(digit_font)
        fm = p.fontMetrics()
        baseline = h - pad_y - fm.descent()

        if self._unit:
            p.setFont(self._unit_font)
            unit_colour = QColor(fg)
            unit_colour.setAlphaF(0.8)
            p.setPen(unit_colour)
            right -= p.fontMetrics().horizontalAdvance(self._unit)
            p.drawText(right, baseline, self._unit)
            right -= theme.SPACE_6

        p.setFont(digit_font)
        text = self._text()
        x = right - fm.horizontalAdvance(text)
        if not self._off:
            # a lit segment bleeds - the one soft effect the system allows
            glow = QColor(fg)
            glow.setAlpha(70)
            p.setPen(glow)
            g = theme.px(1)
            for dx, dy in ((-g, 0), (g, 0), (0, -g), (0, g), (-g, -g), (g, g)):
                p.drawText(x + dx, baseline + dy, text)
        p.setPen(fg)
        p.drawText(x, baseline, text)

        _scanlines(p, w, h)
        p.end()


class Led(QWidget):
    """An indicator lamp with dim / lit / blinking states."""

    def __init__(self, label: str = "", colour: str = "green",
                 diameter: int | None = None, parent=None):
        super().__init__(parent)
        self._label = label
        self._colour = colour
        self._d = theme.px(10) if diameter is None else diameter
        self._on = False
        self._blink = False
        self._phase = True
        self._timer = QTimer(self)
        self._timer.setInterval(theme.DUR_BLINK)
        self._timer.timeout.connect(self._tick)
        self.setFont(theme.ui_font())
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

    def set_on(self, on: bool, blink: bool = False) -> None:
        self._on = on
        self._blink = blink
        self._phase = True
        if on and blink:
            self._timer.start()
        else:
            self._timer.stop()
        self.update()

    def _tick(self) -> None:
        self._phase = not self._phase
        self.update()

    def sizeHint(self):
        fm = QFontMetrics(self.font())
        inset = theme.px(2)
        width = self._d + (theme.SPACE_6 + fm.horizontalAdvance(self._label)
                           if self._label else 0)
        return QSize(width + inset, max(self._d + inset, fm.height()))

    def paintEvent(self, event) -> None:
        lit, dim, _ = _LED_COLOURS[self._colour]
        showing = self._on and (self._phase or not self._blink)
        inset = theme.px(1)
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        y = (self.height() - self._d) // 2
        p.setPen(QColor(theme.GREY_500))
        p.setBrush(QColor(lit if showing else dim))
        p.drawEllipse(inset, y, self._d, self._d)
        if showing:
            highlight = QColor(255, 255, 255, 140)
            spot = max(inset * 2, self._d // 3)
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(highlight)
            p.drawEllipse(inset * 3, y + inset * 2, spot, spot)
        if self._label:
            p.setRenderHint(QPainter.RenderHint.Antialiasing, False)
            p.setPen(QColor(theme.BLACK))
            p.setFont(self.font())
            fm = p.fontMetrics()
            p.drawText(self._d + theme.SPACE_6 + inset * 2,
                       (self.height() + fm.ascent() - fm.descent()) // 2,
                       self._label)
        p.end()


class StatusPane(QLabel):
    """One etched pane of the status bar. Two words maximum, per the system."""

    def __init__(self, text: str = "", width: int = 0, grow: bool = False,
                 parent=None):
        super().__init__(text, parent)
        self._apply_style(theme.BLACK)
        self.setFixedHeight(theme.STATUSBAR_H - theme.BEVEL)
        if width:
            # `width` is a design-pixel figure, like every other token here.
            self.setFixedWidth(theme.px(width))
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding if grow else QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.Fixed)

    def _apply_style(self, colour: str) -> None:
        self.setStyleSheet(
            theme.border_image("bevel_in_thin", thin=True)
            + f"padding: 0 {theme.SPACE_4}px;"
            f"background: {theme.SURFACE_WINDOW}; color: {colour};")

    def set_tone(self, tone: str = "") -> None:
        """`danger` is the only tone the system colours status text with."""
        self._apply_style(theme.STATUS_DANGER if tone == "danger" else theme.BLACK)
