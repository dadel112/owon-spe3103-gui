"""Starts the application. With --demo everything runs against a simulated
supply, no hardware and no free COM port required."""

import argparse
import sys

from PyQt6.QtWidgets import QApplication

from owon_spe3103.gui import MainWindow


def main() -> int:
    parser = argparse.ArgumentParser(description="OWON SPE3103 Steuerung")
    parser.add_argument("--demo", action="store_true",
                        help="simuliertes Geraet statt echter VISA-Verbindung")
    args = parser.parse_args()

    app = QApplication(sys.argv)
    win = MainWindow(demo=args.demo)
    win.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
