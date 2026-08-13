"""Bench95 theme - the design system from design/bench95 ported to Qt.

The design system draws its whole depth vocabulary with hard 1px and 2px inset
box-shadows. Qt stylesheets have no box-shadow, so the bevels are rendered once
into small nine-slice PNGs and handed to QSS as `border-image`. That keeps the
edges pixel-exact instead of approximating them with Qt's own 3D border styles.

Everything else - colours, metrics, type - is a straight port of the token
files. Keep the constants below in sync with design/bench95/tokens/*.css.

Every metric is authored against the design system's 96 dpi grid. `apply()`
rescales the whole set for the display it lands on, so nothing below is a
pixel value that reaches the screen unchanged - read scale() before using one.
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path
from string import Template

from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import (QColor, QFont, QFontDatabase, QImage, QPainter,
                         QPolygonF)

# -- tokens/colors.css ---------------------------------------------------
GREY_WHITE = "#ffffff"
GREY_100 = "#dfdfdf"
GREY_200 = "#d4d0c8"
GREY_300 = "#c0c0c0"
GREY_400 = "#a0a0a0"
GREY_500 = "#808080"
GREY_700 = "#404040"
BLACK = "#000000"

NAVY_900 = "#000080"
BLUE_500 = "#1084d0"

LED_GREEN = "#22ff66"
LED_GREEN_DIM = "#0d5c26"
LED_AMBER = "#ffb000"
LED_AMBER_DIM = "#5c3f00"
LED_RED = "#ff3b30"
LED_RED_DIM = "#5c0f0c"
READOUT_BG = "#0b1a0f"
READOUT_BG_AMBER = "#1a1200"
CRT_LINE = QColor(0, 0, 0, 71)          # rgba(0,0,0,.28)

STATUS_OK = "#008000"
STATUS_WARN = "#ffb000"
STATUS_DANGER = "#c00000"

SURFACE_WINDOW = GREY_300
SURFACE_FIELD = GREY_WHITE
SURFACE_TROUGH = GREY_100
SURFACE_SELECTED = NAVY_900
TEXT_DISABLED = GREY_500
TOOLTIP_BG = "#ffffe1"

# -- tokens/spacing.css --------------------------------------------------
SPACE_2, SPACE_3, SPACE_4, SPACE_6 = 2, 3, 4, 6
SPACE_8, SPACE_11, SPACE_16, SPACE_24 = 8, 11, 16, 24
CONTROL_H_SM = 18
CONTROL_H = 21
CONTROL_H_BTN = 23
CONTROL_H_LG = 26
BTN_MIN_W = 75
MENUBAR_H = 19
STATUSBAR_H = 20
SCROLLBAR = 16

# The chrome's own hairlines, previously spelled out as literals in the QSS.
BEVEL = 2               # the 2px raised/sunken edge
BEVEL_THIN = 1          # the 1px etched edge
SPIN_COL_W = 17         # the spinner's arrow column
ARROW_W, ARROW_H = 7, 4
CHECK_BOX = 13
RADIO_BOX = 12
SLIDER_GROOVE_H = 4
SLIDER_HANDLE_W = 11
SLIDER_H = 20
GROUPBOX_GAP = 7        # how far the caption lifts off the frame

# -- tokens/typography.css ----------------------------------------------
# MS Sans Serif is the authentic face. It is self-hosted in the design system,
# and anything found in design/bench95/fonts wins. Windows' own copy is the
# legacy bitmap font, which only holds a handful of sizes and scales badly, so
# the TrueType Microsoft Sans Serif comes first among the system faces.
FONT_UI_STACK = ['MS Sans Serif', 'Microsoft Sans Serif', 'Tahoma', 'Verdana']
FONT_UI_SYSTEM = ['Microsoft Sans Serif', 'MS Sans Serif', 'Tahoma', 'Verdana']
FONT_MONO_STACK = ['VT323', 'Lucida Console', 'Consolas', 'Courier New']
FONT_PIXEL_STACK = ['Silkscreen', 'Small Fonts', 'Tahoma']

TEXT_2XS = 9
TEXT_XS = 10
TEXT_SM = 11        # the entire UI is authored on an 11px body
TEXT_LG = 13
TEXT_READOUT_SM = 20
TEXT_READOUT_MD = 32
TEXT_READOUT_LG = 48

# -- tokens/motion.css ---------------------------------------------------
DUR_BLINK = 530     # the classic alarm-lamp interval


# -- display scaling -----------------------------------------------------
# Names whose value is a length. apply() multiplies every one of them by the
# scale the display asks for; everything else in the module is a colour, a
# duration or a font family and stays put.
_METRICS = (
    "SPACE_2", "SPACE_3", "SPACE_4", "SPACE_6", "SPACE_8", "SPACE_11",
    "SPACE_16", "SPACE_24", "CONTROL_H_SM", "CONTROL_H", "CONTROL_H_BTN",
    "CONTROL_H_LG", "BTN_MIN_W", "MENUBAR_H", "STATUSBAR_H", "SCROLLBAR",
    "BEVEL", "BEVEL_THIN", "SPIN_COL_W", "ARROW_W", "ARROW_H", "CHECK_BOX",
    "RADIO_BOX", "SLIDER_GROOVE_H", "SLIDER_HANDLE_W", "SLIDER_H",
    "GROUPBOX_GAP", "TEXT_2XS", "TEXT_XS", "TEXT_SM", "TEXT_LG",
    "TEXT_READOUT_SM", "TEXT_READOUT_MD", "TEXT_READOUT_LG",
)
_BASE = {name: globals()[name] for name in _METRICS}

UI_SCALE_ENV = "BENCH95_UI_SCALE"

_scale = 1.0        # design pixels -> logical pixels
_dpr = 1.0          # logical pixels -> device pixels, Qt's own factor


def scale() -> float:
    """How far the 96 dpi design grid has been stretched for this display."""
    return _scale


def px(value: float) -> int:
    """A design-pixel length in logical pixels at the current scale."""
    return max(1, round(value * _scale))


def _detect_scale(app) -> float:
    """Work out how much the design grid has to grow on this display.

    Qt already multiplies every logical pixel by the screen's device pixel
    ratio, so Windows' own 125 %/150 % scaling is handled before we get here.
    What Qt cannot know is that this design is drawn for a 96 dpi grid: on a
    dense laptop panel left at 100 %, a 21 px control comes out half the size
    it was drawn for. Qt reports the physical dpi already divided by the device
    pixel ratio, so that figure against 96 is exactly what is left to make up.

    Quarter steps only, and never below the authored size - the metrics are
    small integers and a 1.1x factor would blur them for no gain.
    """
    override = os.environ.get(UI_SCALE_ENV)
    if override:
        try:
            return min(3.0, max(1.0, float(override)))
        except ValueError:
            pass
    screen = app.primaryScreen()
    if screen is None:
        return 1.0
    residual = screen.physicalDotsPerInch() / 96.0
    for step in (2.0, 1.75, 1.5, 1.25):
        if residual >= step:
            return step
    return 1.0


def _rescale(factor: float, dpr: float) -> None:
    """Restate every metric token at `factor`, and remember the device ratio so
    the generated tiles can be drawn at the screen's real resolution."""
    global _scale, _dpr
    _scale, _dpr = factor, dpr
    g = globals()
    for name, base in _BASE.items():
        g[name] = max(1, round(base * factor))


def _ipx(design: float) -> int:
    """A design-pixel length in *image* pixels of a generated tile.

    A tile slice of n image pixels is painted into a border n/_dpr logical
    pixels wide, so rendering at scale x device ratio keeps the nine-slice
    landing on whole device pixels instead of being stretched into mush.
    """
    return max(1, round(design * _scale * _dpr))


def _dev(logical: float) -> int:
    """An already-scaled token length in image pixels of a generated tile."""
    return max(1, round(logical * _dpr))


def _cache_dir() -> Path:
    d = Path(tempfile.gettempdir()) / "bench95_theme"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _blank(w: int, h: int | None = None) -> QImage:
    img = QImage(w, h if h is not None else w, QImage.Format.Format_ARGB32)
    img.fill(Qt.GlobalColor.transparent)
    return img


def _save(name: str, img: QImage) -> str:
    """Write a tile under a scale-stamped name, so a run at one scale never
    picks up the cached tile another run left behind.

    Plain letters, digits and dashes only: the path goes into a QSS url(),
    which is CSS and takes '@' as the start of an at-rule - a tile named for
    its scale the obvious way silently fails to load and the whole chrome
    comes out flat.
    """
    path = _cache_dir() / f"{name}-{round(_scale * 100)}-{round(_dpr * 100)}.png"
    img.save(str(path))
    return path.as_posix()


def _bevel(name: str, layers: list[tuple[int, str, str]]) -> str:
    """Render one nine-slice bevel tile and return its path.

    `layers` is the token's box-shadow list in *reverse* declaration order, so
    the last entry ends up on top exactly as CSS paints it. Each layer is
    (thickness, "tl"|"br", colour) in design pixels; the tile's centre stays
    transparent so the widget's own background-color shows through.
    """
    edge = _ipx(max(t for t, _, _ in layers))
    size = 2 * edge + 2
    img = _blank(size)
    p = QPainter(img)
    p.setCompositionMode(QPainter.CompositionMode.CompositionMode_Source)
    for thickness, side, colour in layers:
        t = _ipx(thickness)
        c = QColor(colour)
        if side == "tl":
            p.fillRect(0, 0, size, t, c)
            p.fillRect(0, 0, t, size, c)
        else:
            p.fillRect(0, size - t, size, t, c)
            p.fillRect(size - t, 0, t, size, c)
    p.end()
    return _save(name, img)


def _arrow(name: str, direction: str, colour: str) -> str:
    """The 3px solid triangles the spinners and scrollbars use.

    Drawn at the tile resolution rather than at 7x4 and left for Qt to blow up
    - an upscaled triangle is the mush that made the spinner arrows look
    squashed on anything but a 1:1 display.
    """
    long_side, short_side = _dev(ARROW_W), _dev(ARROW_H)
    w, h = ((long_side, short_side) if direction in ("up", "down")
            else (short_side, long_side))
    img = _blank(w, h)
    p = QPainter(img)
    p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    # The triangle spans the tile; the polygon below is the token's shape
    # expressed as fractions of it, so it stays the same wedge at every size.
    unit = {
        "down": [(0, 0), (1, 0), (0.5, 1)],
        "up": [(0.5, 0), (0, 1), (1, 1)],
        "right": [(0, 0), (0, 1), (1, 0.5)],
        "left": [(1, 0), (1, 1), (0, 0.5)],
    }[direction]
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QColor(colour))
    p.drawPolygon(QPolygonF([QPointF(x * (w - 1), y * (h - 1)) for x, y in unit]))
    p.end()
    return _save(name, img)


def _checkbox(name: str, checked: bool, enabled: bool = True) -> str:
    """13px sunken box with the 2px tick, drawn by hand so it stays crunchy."""
    size = _dev(CHECK_BOX)
    k = size / 13.0                 # the tick below is plotted on the 13px grid
    img = _blank(size)
    p = QPainter(img)
    p.setCompositionMode(QPainter.CompositionMode.CompositionMode_Source)
    p.fillRect(0, 0, size, size, QColor(SURFACE_FIELD if enabled else GREY_300))
    for thickness, side, colour in _BEVEL_IN:
        t = _ipx(thickness)
        c = QColor(colour)
        if side == "tl":
            p.fillRect(0, 0, size, t, c)
            p.fillRect(0, 0, t, size, c)
        else:
            p.fillRect(0, size - t, size, t, c)
            p.fillRect(size - t, 0, t, size, c)
    if checked:
        p.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
        c = QColor(BLACK if enabled else GREY_500)
        # the classic tick: two strokes, plotted per pixel column
        for x, y in ((3, 5), (4, 6), (5, 7), (6, 6), (7, 5), (8, 4), (9, 3)):
            p.fillRect(QRectF(x * k, y * k, k, 2 * k), c)
    p.end()
    return _save(name, img)


def _radio(name: str, checked: bool, enabled: bool = True) -> str:
    """12px round bevel with a 4px dot - round only because the hardware is."""
    size = _dev(RADIO_BOX)
    k = size / 12.0
    img = _blank(size)
    p = QPainter(img)
    p.setRenderHint(QPainter.RenderHint.Antialiasing, size > 12)
    p.setBrush(QColor(SURFACE_FIELD if enabled else GREY_300))
    p.setPen(QColor(GREY_500))
    p.drawEllipse(0, 0, size - 1, size - 1)
    p.setPen(QColor(BLACK))
    p.drawArc(0, 0, size - 1, size - 1, 45 * 16, 180 * 16)
    p.setPen(QColor(GREY_WHITE))
    p.drawArc(0, 0, size - 1, size - 1, 225 * 16, 180 * 16)
    if checked:
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(BLACK if enabled else GREY_500))
        p.drawEllipse(QRectF(4 * k, 4 * k, 4 * k, 4 * k))
    p.end()
    return _save(name, img)


def _checker(name: str) -> str:
    """--pattern-checker: the 2px checkerboard used for scrollbar troughs and
    latched button faces.

    Qt repeats a background-image at its own pixel size in logical coordinates,
    so this one grows with the design scale but not with the device ratio.
    """
    cell = px(1)
    size = 2 * cell
    img = QImage(size, size, QImage.Format.Format_ARGB32)
    p = QPainter(img)
    p.setCompositionMode(QPainter.CompositionMode.CompositionMode_Source)
    p.fillRect(0, 0, size, size, QColor(GREY_100))
    p.fillRect(0, 0, cell, cell, QColor(GREY_WHITE))
    p.fillRect(cell, cell, cell, cell, QColor(GREY_WHITE))
    p.end()
    return _save(name, img)


# The four bevels, transcribed from tokens/bevels.css in reverse declaration
# order (CSS paints the first-declared shadow on top).
_BEVEL_OUT = [(2, "tl", GREY_100), (2, "br", GREY_500),
              (1, "tl", GREY_WHITE), (1, "br", BLACK)]
_BEVEL_OUT_PRESSED = [(2, "tl", BLACK), (1, "tl", GREY_500)]
_BEVEL_IN = [(2, "tl", BLACK), (2, "br", GREY_100),
             (1, "tl", GREY_500), (1, "br", GREY_WHITE)]
_BEVEL_OUT_THIN = [(1, "tl", GREY_WHITE), (1, "br", GREY_500)]
_BEVEL_IN_THIN = [(1, "tl", GREY_500), (1, "br", GREY_WHITE)]
_OUTLINE = [(1, "tl", BLACK), (1, "br", BLACK)]

_BEVELS = {
    "out": _BEVEL_OUT, "out_pressed": _BEVEL_OUT_PRESSED, "in": _BEVEL_IN,
    "out_thin": _BEVEL_OUT_THIN, "in_thin": _BEVEL_IN_THIN, "outline": _OUTLINE,
}

_assets: dict[str, str] = {}


def border_image(asset: str, thin: bool = False) -> str:
    """The QSS for one of the generated nine-slice bevels, for the widgets that
    style themselves outside the application stylesheet.

    The slice is quoted in image pixels and the border width in logical ones,
    so the two have to be derived together - the tiles are rendered at the
    display's own resolution, not at the design's 96 dpi.
    """
    s = _ipx(1 if thin else 2)
    width = BEVEL_THIN if thin else BEVEL
    return (f"border-image: url({assets()[asset]}) {s} {s} {s} {s} "
            f"stretch stretch; border-width: {width}px;")


def bevel_layers(name: str) -> list[tuple[int, str, str]]:
    """A bevel's shadow layers with their thicknesses in logical pixels, for
    the widgets that paint their own well instead of going through QSS."""
    return [(px(thickness), side, colour)
            for thickness, side, colour in _BEVELS[name]]


def assets() -> dict[str, str]:
    """Render (once) and return every generated tile, keyed by name."""
    if _assets:
        return _assets
    _assets.update(
        bevel_out=_bevel("bevel_out", _BEVEL_OUT),
        bevel_out_pressed=_bevel("bevel_out_pressed", _BEVEL_OUT_PRESSED),
        bevel_in=_bevel("bevel_in", _BEVEL_IN),
        bevel_out_thin=_bevel("bevel_out_thin", _BEVEL_OUT_THIN),
        bevel_in_thin=_bevel("bevel_in_thin", _BEVEL_IN_THIN),
        outline=_bevel("outline", _OUTLINE),
        arrow_down=_arrow("arrow_down", "down", BLACK),
        arrow_up=_arrow("arrow_up", "up", BLACK),
        arrow_left=_arrow("arrow_left", "left", BLACK),
        arrow_right=_arrow("arrow_right", "right", BLACK),
        arrow_down_off=_arrow("arrow_down_off", "down", GREY_500),
        arrow_up_off=_arrow("arrow_up_off", "up", GREY_500),
        check_off=_checkbox("check_off", False),
        check_on=_checkbox("check_on", True),
        check_off_dis=_checkbox("check_off_dis", False, False),
        check_on_dis=_checkbox("check_on_dis", True, False),
        radio_off=_radio("radio_off", False),
        radio_on=_radio("radio_on", True),
        radio_off_dis=_radio("radio_off_dis", False, False),
        checker=_checker("checker"),
    )
    return _assets


_QSS = Template("""
/* ---- base: one neutral chrome carries 95% of the pixels ---- */
QWidget {
    background: $window;
    color: $text;
    font-family: "$font_ui";
    font-size: ${text_sm}px;
}
QMainWindow, QDialog { background: $window; }
QWidget:disabled { color: $disabled; }

QLabel, QCheckBox, QRadioButton { background: transparent; }
QLabel:disabled, QCheckBox:disabled, QRadioButton:disabled { color: $disabled; }

/* ---- group box: the etched frame with its caption breaking the top rule ---- */
QGroupBox {
    border-image: url($bevel_in_thin) $s1 $s1 $s1 $s1 stretch stretch;
    border-width: ${bevel_thin}px;
    margin-top: ${gb_gap}px;
    padding: ${space_11}px ${space_8}px ${space_8}px ${space_8}px;
    background: transparent;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: ${space_8}px;
    padding: 0 ${space_4}px;
    background: $window;
    color: $text;
}

/* ---- push button: raised, inverts on press, never reacts to hover ---- */
QPushButton {
    border-image: url($bevel_out) $s2 $s2 $s2 $s2 stretch stretch;
    border-width: ${bevel}px;
    background: $window;
    min-width: ${btn_min_w}px;
    min-height: ${btn_inner}px;    /* + the bevel top and bottom = ${btn_h}px */
    padding: 0 ${space_8}px;
}
QPushButton:pressed, QPushButton:checked {
    border-image: url($bevel_out_pressed) $s2 $s2 $s2 $s2 stretch stretch;
    padding: ${bevel}px ${space_8}px 0 ${space_8}px;   /* the label nudges in */
}
QPushButton:disabled { color: $disabled; }
QPushButton:default {
    border-image: url($bevel_out) $s2 $s2 $s2 $s2 stretch stretch;
}
QPushButton:focus { outline: none; }

/* ---- tool button: the square bevelled tool button, latches when active ---- */
QToolButton {
    border-image: url($bevel_out) $s2 $s2 $s2 $s2 stretch stretch;
    border-width: ${bevel}px;
    background: $window;
    padding: ${space_2}px ${space_6}px;
    min-height: ${btn_inner}px;
}
QToolButton:pressed, QToolButton:checked {
    border-image: url($bevel_out_pressed) $s2 $s2 $s2 $s2 stretch stretch;
    background-image: url($checker);
    background-repeat: repeat;
    padding: ${space_3}px ${space_6}px ${bevel_thin}px ${space_6}px;
}
QToolButton:disabled { color: $disabled; }

QToolBar {
    border-image: url($bevel_out_thin) $s1 $s1 $s1 $s1 stretch stretch;
    border-width: ${bevel_thin}px;
    background: $window;
    padding: ${space_2}px;
    spacing: ${space_2}px;
}
QToolBar::separator {
    background: $grey_500;
    width: ${bevel_thin}px;
    margin: ${space_2}px ${space_4}px;
}

/* ---- sunken content: anything you read or type into ---- */
QLineEdit, QPlainTextEdit, QTextEdit, QListView, QTreeView, QTableView, QListWidget {
    border-image: url($bevel_in) $s2 $s2 $s2 $s2 stretch stretch;
    border-width: ${bevel}px;
    background: $field;
    selection-background-color: $selected;
    selection-color: $grey_white;
    padding: ${space_2}px;
}
/* The era's control heights are fixed, not derived from the font. Every inner
   height below is the token height minus the bevel on each edge. */
QLineEdit {
    min-height: ${ctl_inner}px;
    max-height: ${ctl_inner}px;
    padding: 0 ${space_3}px;
}
QLineEdit:disabled, QPlainTextEdit:disabled { background: $window; color: $disabled; }

/* ---- spin box: mono right-aligned value, stacked arrows ---- */
QAbstractSpinBox {
    border-image: url($bevel_in) $s2 $s2 $s2 $s2 stretch stretch;
    border-width: ${bevel}px;
    background: $field;
    min-height: ${ctl_inner}px;
    max-height: ${ctl_inner}px;
    padding: 0 ${spin_pad}px 0 ${space_3}px;   /* arrow column + inset */
    font-family: "$font_mono";
    font-size: ${text_lg}px;
}
QAbstractSpinBox:disabled { background: $window; color: $disabled; }
/* The arrow column is a sibling of the field, not part of it, so the two
   buttons get explicit sizes - a percentage here is not honoured. Qt reads a
   sub-control's width and height as its *content* box and adds the border on
   top, so both figures below are the token size less the bevel on each edge.
   Get that wrong and the two buttons come out four bevels too tall between
   them, overlap inside the field, and the top arrow is squashed into whatever
   the bottom one leaves of it - worse the higher the device pixel ratio. */
QAbstractSpinBox::up-button, QAbstractSpinBox::down-button {
    border-image: url($bevel_out) $s2 $s2 $s2 $s2 stretch stretch;
    border-width: ${bevel}px;
    background: $window;
    width: ${spin_col_w}px;
    subcontrol-origin: border;
}
QAbstractSpinBox::up-button {
    height: ${spin_up_h}px;
    subcontrol-position: top right;
}
QAbstractSpinBox::down-button {
    height: ${spin_down_h}px;
    subcontrol-position: bottom right;
}
QAbstractSpinBox::up-button:pressed, QAbstractSpinBox::down-button:pressed {
    border-image: url($bevel_out_pressed) $s2 $s2 $s2 $s2 stretch stretch;
}
QAbstractSpinBox::up-arrow {
    image: url($arrow_up); width: ${arrow_w}px; height: ${arrow_h}px;
}
QAbstractSpinBox::down-arrow {
    image: url($arrow_down); width: ${arrow_w}px; height: ${arrow_h}px;
}
QAbstractSpinBox::up-arrow:disabled, QAbstractSpinBox::up-arrow:off { image: url($arrow_up_off); }
QAbstractSpinBox::down-arrow:disabled, QAbstractSpinBox::down-arrow:off { image: url($arrow_down_off); }

/* ---- combo box: sunken field, raised drop button, hard-outlined list ---- */
QComboBox {
    border-image: url($bevel_in) $s2 $s2 $s2 $s2 stretch stretch;
    border-width: ${bevel}px;
    background: $field;
    min-height: ${ctl_inner}px;
    max-height: ${ctl_inner}px;
    padding: 0 ${combo_pad}px 0 ${space_3}px;
}
QComboBox:disabled { background: $window; color: $disabled; }
QComboBox::drop-down {
    border-image: url($bevel_out) $s2 $s2 $s2 $s2 stretch stretch;
    border-width: ${bevel}px;
    background: $window;
    width: ${combo_btn_w}px;    /* content box; + the bevel = ${scrollbar}px */
    subcontrol-origin: border;
    subcontrol-position: center right;
}
QComboBox::down-arrow {
    image: url($arrow_down); width: ${arrow_w}px; height: ${arrow_h}px;
}
QComboBox::down-arrow:disabled { image: url($arrow_down_off); }
QComboBox QAbstractItemView {
    border-image: url($outline) $s1 $s1 $s1 $s1 stretch stretch;
    border-width: ${bevel_thin}px;
    background: $field;
    selection-background-color: $selected;
    selection-color: $grey_white;
    outline: none;
}

/* ---- checkbox / radio: hand-drawn indicators, no rounding anywhere ---- */
QCheckBox::indicator {
    width: ${check_box}px; height: ${check_box}px; image: url($check_off);
}
QCheckBox::indicator:checked { image: url($check_on); }
QCheckBox::indicator:disabled { image: url($check_off_dis); }
QCheckBox::indicator:checked:disabled { image: url($check_on_dis); }
QCheckBox { spacing: ${space_6}px; }
QRadioButton::indicator {
    width: ${radio_box}px; height: ${radio_box}px; image: url($radio_off);
}
QRadioButton::indicator:checked { image: url($radio_on); }
QRadioButton::indicator:disabled { image: url($radio_off_dis); }
QRadioButton { spacing: ${space_6}px; }

/* ---- slider: etched trough, raised thumb ---- */
QSlider::groove:horizontal {
    border-image: url($bevel_in_thin) $s1 $s1 $s1 $s1 stretch stretch;
    border-width: ${bevel_thin}px;
    background: $trough;
    height: ${slider_groove_h}px;
    margin: 0 ${slider_mh}px;
}
QSlider::handle:horizontal {
    border-image: url($bevel_out) $s2 $s2 $s2 $s2 stretch stretch;
    border-width: ${bevel}px;
    background: $window;
    width: ${slider_handle_w}px;
    margin: -${slider_mv}px -${slider_mh}px;
}
QSlider::handle:horizontal:disabled { background: $grey_100; }
QSlider { min-height: ${slider_h}px; }

/* ---- scrollbars: 16px, checkered trough, raised thumb and end buttons ---- */
QScrollBar:vertical, QScrollBar:horizontal {
    background-image: url($checker);
    background-repeat: repeat;
    border: 0;
}
QScrollBar:vertical { width: ${scrollbar}px; }
QScrollBar:horizontal { height: ${scrollbar}px; }
QScrollBar::handle {
    border-image: url($bevel_out) $s2 $s2 $s2 $s2 stretch stretch;
    border-width: ${bevel}px;
    background: $window;
}
QScrollBar::handle:vertical { min-height: ${scrollbar}px; }
QScrollBar::handle:horizontal { min-width: ${scrollbar}px; }
QScrollBar::add-line, QScrollBar::sub-line {
    border-image: url($bevel_out) $s2 $s2 $s2 $s2 stretch stretch;
    border-width: ${bevel}px;
    background: $window;
    subcontrol-origin: margin;
}
QScrollBar::add-line:vertical { height: ${scrollbar}px; subcontrol-position: bottom; }
QScrollBar::sub-line:vertical { height: ${scrollbar}px; subcontrol-position: top; }
QScrollBar::add-line:horizontal { width: ${scrollbar}px; subcontrol-position: right; }
QScrollBar::sub-line:horizontal { width: ${scrollbar}px; subcontrol-position: left; }
QScrollBar::up-arrow:vertical {
    image: url($arrow_up); width: ${arrow_w}px; height: ${arrow_h}px;
}
QScrollBar::down-arrow:vertical {
    image: url($arrow_down); width: ${arrow_w}px; height: ${arrow_h}px;
}
QScrollBar::left-arrow:horizontal {
    image: url($arrow_left); width: ${arrow_h}px; height: ${arrow_w}px;
}
QScrollBar::right-arrow:horizontal {
    image: url($arrow_right); width: ${arrow_h}px; height: ${arrow_w}px;
}
QScrollBar::add-page, QScrollBar::sub-page { background: transparent; }

/* ---- menus: navy fill and white text, instantly, no hover fade ---- */
QMenuBar {
    background: $window;
    min-height: ${menubar_h}px;
    border: 0;
}
QMenuBar::item { background: transparent; padding: ${space_3}px ${space_8}px; }
QMenuBar::item:selected, QMenuBar::item:pressed {
    background: $selected;
    color: $grey_white;
}
QMenu {
    border-image: url($outline) $s1 $s1 $s1 $s1 stretch stretch;
    border-width: ${bevel_thin}px;
    background: $window;
    padding: ${space_2}px;
}
QMenu::item {
    padding: ${space_3}px ${space_24}px ${space_3}px ${space_16}px;
    background: transparent;
}
QMenu::item:selected { background: $selected; color: $grey_white; }
QMenu::item:disabled { color: $disabled; }
QMenu::separator {
    height: ${bevel}px;
    margin: ${space_2}px ${space_2}px;
    border-image: url($bevel_in_thin) $s1 $s1 $s1 $s1 stretch stretch;
    border-width: ${bevel_thin}px;
}

/* ---- status bar: etched panes along the bottom edge ---- */
QStatusBar {
    background: $window;
    min-height: ${statusbar_h}px;
}
QStatusBar::item { border: 0; }

/* ---- property-sheet tabs: the active tab grows into the page ---- */
QTabWidget::pane {
    border-image: url($bevel_out_thin) $s1 $s1 $s1 $s1 stretch stretch;
    border-width: ${bevel_thin}px;
    background: $window;
    top: -${bevel_thin}px;
}
QTabBar::tab {
    border-image: url($bevel_out_thin) $s1 $s1 $s1 $s1 stretch stretch;
    border-width: ${bevel_thin}px;
    background: $window;
    padding: ${space_3}px ${space_8}px;
    margin-right: ${bevel_thin}px;
}
QTabBar::tab:selected {
    padding: ${space_4}px ${space_11}px ${space_4}px ${space_11}px;
    margin-top: -${bevel}px;
}

/* ---- progress: a navy fill stepping through a sunken trough ---- */
QProgressBar {
    border-image: url($bevel_in) $s2 $s2 $s2 $s2 stretch stretch;
    border-width: ${bevel}px;
    background: $window;
    text-align: center;
}
QProgressBar::chunk {
    background: $selected; margin: ${bevel_thin}px; width: ${space_8}px;
}

/* ---- tooltip: pale yellow balloon, black outline, instant ---- */
QToolTip {
    background: $tooltip;
    color: $text;
    border: ${bevel_thin}px solid $black;
    padding: ${space_2}px ${space_4}px;
}

/* ---- headers on report-view lists: sticky and raised ---- */
QHeaderView::section {
    border-image: url($bevel_out) $s2 $s2 $s2 $s2 stretch stretch;
    border-width: ${bevel}px;
    background: $window;
    padding: ${space_2}px ${space_4}px;
}

QSplitter::handle { background: $window; }
QScrollArea { border: 0; background: $window; }
""")


def stylesheet() -> str:
    a = assets()
    # Sub-control width/height are content boxes, so every figure handed to one
    # is the token size less its bevel on each edge. The two spinner buttons
    # have to tile the field's border box exactly; the odd row goes to the top
    # one rather than being left over as a seam.
    spin_h = max(2, CONTROL_H - 4 * BEVEL)
    spin_up = (spin_h + 1) // 2
    return _QSS.substitute(
        window=SURFACE_WINDOW, field=SURFACE_FIELD, trough=SURFACE_TROUGH,
        selected=SURFACE_SELECTED, text=BLACK, black=BLACK,
        disabled=TEXT_DISABLED, grey_white=GREY_WHITE, grey_100=GREY_100,
        grey_500=GREY_500, tooltip=TOOLTIP_BG,
        font_ui=ui_family(), font_mono=mono_family(),
        text_sm=TEXT_SM, text_lg=TEXT_LG,
        space_2=SPACE_2, space_3=SPACE_3, space_4=SPACE_4, space_6=SPACE_6,
        space_8=SPACE_8, space_11=SPACE_11, space_16=SPACE_16,
        space_24=SPACE_24,
        # nine-slice widths: the tiles are rendered at the device resolution,
        # so a slice is the bevel in device pixels, not in design pixels.
        s1=_ipx(1), s2=_ipx(2), bevel=BEVEL, bevel_thin=BEVEL_THIN,
        btn_min_w=BTN_MIN_W, btn_h=CONTROL_H_BTN,
        btn_inner=CONTROL_H_BTN - 2 * BEVEL,
        ctl_h=CONTROL_H, ctl_inner=CONTROL_H - 2 * BEVEL,
        spin_col_w=max(1, SPIN_COL_W - 2 * BEVEL), spin_up_h=spin_up,
        spin_down_h=spin_h - spin_up, spin_pad=SPIN_COL_W + SPACE_3,
        combo_btn_w=max(1, SCROLLBAR - 2 * BEVEL),
        combo_pad=SCROLLBAR + SPACE_3,
        arrow_w=ARROW_W, arrow_h=ARROW_H,
        check_box=CHECK_BOX, radio_box=RADIO_BOX,
        slider_groove_h=SLIDER_GROOVE_H, slider_handle_w=SLIDER_HANDLE_W,
        slider_h=SLIDER_H,
        slider_mh=max(1, (SLIDER_HANDLE_W - 1) // 2),
        slider_mv=max(1, (SLIDER_H - SLIDER_GROOVE_H) // 2),
        gb_gap=GROUPBOX_GAP, menubar_h=MENUBAR_H,
        statusbar_h=STATUSBAR_H, scrollbar=SCROLLBAR,
        **a,
    )


# -- fonts ---------------------------------------------------------------
_families: dict[str, str] = {}
_bundled: list[str] = []


def _load_bundled_fonts() -> None:
    """Pick up any font the design system ships with, if it has been imported.

    design/bench95/fonts/ is where the system self-hosts MS Sans Serif; drop
    VT323 or Silkscreen next to it and the readouts and captions pick them up.
    """
    _bundled.clear()
    font_dir = Path(__file__).resolve().parent.parent / "design" / "bench95" / "fonts"
    if not font_dir.is_dir():
        return
    for path in sorted(font_dir.glob("*.ttf")) + sorted(font_dir.glob("*.otf")):
        font_id = QFontDatabase.addApplicationFont(str(path))
        if font_id != -1:
            _bundled.extend(QFontDatabase.applicationFontFamilies(font_id))


def _first_available(stack: list[str], fallback: str) -> str:
    """A font imported with the design system beats the system's own copy."""
    for family in _bundled:
        if family in stack:
            return family
    installed = set(QFontDatabase.families())
    for family in stack:
        if family in installed:
            return family
    return fallback


def ui_family() -> str:
    if "ui" not in _families:
        _families["ui"] = _first_available(FONT_UI_SYSTEM, "Tahoma")
    return _families["ui"]


def mono_family() -> str:
    if "mono" not in _families:
        _families["mono"] = _first_available(FONT_MONO_STACK, "Courier New")
    return _families["mono"]


def pixel_family() -> str:
    if "pixel" not in _families:
        _families["pixel"] = _first_available(FONT_PIXEL_STACK, ui_family())
    return _families["pixel"]


# The size defaults below are None rather than the token itself: a default is
# bound once at import, which is before apply() has restated the tokens for the
# display, so a literal default would pin every font to the 96 dpi size.
def ui_font(size: int | None = None, bold: bool = False) -> QFont:
    f = QFont(ui_family(), -1)
    f.setPixelSize(TEXT_SM if size is None else size)
    f.setBold(bold)
    return f


def mono_font(size: int | None = None, bold: bool = False) -> QFont:
    """Antialiasing stays off so the type keeps its crunch, as the era had."""
    f = QFont(mono_family(), -1)
    f.setPixelSize(TEXT_LG if size is None else size)
    f.setBold(bold)
    f.setStyleStrategy(QFont.StyleStrategy.NoAntialias)
    return f


def font_style(family: str, size: int, bold: bool = False) -> str:
    """A per-widget font declaration.

    The application stylesheet sets font-family and font-size on QWidget, and a
    stylesheet always beats setFont(), so anything that needs the mono or a
    larger face has to say so in its own stylesheet.
    """
    weight = "bold" if bold else "normal"
    return (f"font-family: \"{family}\"; font-size: {size}px; "
            f"font-weight: {weight};")


def pixel_font(size: int | None = None) -> QFont:
    f = QFont(pixel_family(), -1)
    f.setPixelSize(TEXT_2XS if size is None else size)
    f.setStyleStrategy(QFont.StyleStrategy.NoAntialias)
    return f


def apply(app) -> None:
    """Install the theme on a QApplication, sized for the display it is on."""
    screen = app.primaryScreen()
    _rescale(_detect_scale(app),
             screen.devicePixelRatio() if screen is not None else 1.0)
    _assets.clear()             # the tiles are rendered for one scale only
    _load_bundled_fonts()
    _families.clear()
    app.setStyle("Fusion")      # a predictable base for the stylesheet to sit on
    app.setFont(ui_font())
    app.setStyleSheet(stylesheet())
