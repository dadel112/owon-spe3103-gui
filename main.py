"""Startet die Anwendung. Mit --demo laeuft alles gegen ein simuliertes Netzteil,
dafuer braucht es weder Hardware noch einen freien COM-Port."""

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
