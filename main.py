"""Starts the application. With --demo everything runs against a simulated
supply, no hardware and no free COM port required."""

import argparse
import sys

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QGuiApplication
from PyQt6.QtWidgets import QApplication

from owon_spe3103 import theme
from owon_spe3103.gui import MainWindow


def main() -> int:
    parser = argparse.ArgumentParser(description="OWON SPE3103 control")
    parser.add_argument("--demo", action="store_true",
                        help="use a simulated device instead of a real VISA connection")
    args = parser.parse_args()

    # Take Windows' 125 %/150 % scaling at face value instead of letting Qt
    # round it to whole steps. This is Qt 6's default, but it has to be set
    # before the QApplication exists, and saying so keeps the window honest if
    # the default ever moves again. theme.apply() makes up whatever is left.
    QGuiApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)

    app = QApplication(sys.argv)
    theme.apply(app)
    win = MainWindow(demo=args.demo)
    win.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
