# OWON SPE3103 GUI

Desktop-Steuerung für OWON SPE3103 (30 V / 10 A) über USB/SCPI, PyVISA + PyQt6 + pyqtgraph.

## Installation
- Python 3.11+, Windows 11
- `python -m venv .venv` + `.venv\Scripts\activate`
- `pip install -r requirements.txt` (kein NI-VISA nötig, Backend `@py`)

## Start
- Normal: `python main.py` → Ressource wählen (z.B. `ASRL3::INSTR`), Baudrate, Connect
- Demo: `python main.py --demo` — simuliertes Gerät, keine Hardware, Buttons zum Erzwingen von OVP/OCP-Trip
- Ausgang wird beim Verbinden nie automatisch eingeschaltet

## Discovery
- Keine verifizierte SCPI-Liste; `scpi_map.py` hält Kandidatenlisten je Funktion
- Beim ersten Verbinden werden Kandidaten getestet (Queries direkt, Sets nur bei Ausgang aus + Readback, Prüfung per `SYST:ERR?`)
- Ergebnis in `scpi_profile.json` neben `main.py`; nicht auflösbare Funktionen sind im GUI als „nicht unterstützt" markiert und deaktiviert

## Schutzstufen
- Stufe 1 Hardware-OVP/OCP: Schwellen setzen/aktivieren, Trip-Abfrage im Poll-Zyklus, sofortiges Aus + Alarmbanner + Log + Ton
- Stufe 2 Software-OVP/OCP: immer aktiv, vergleicht jeden Messwert, Not-Aus mit Queue-Priorität, Ansprechverzögerung 0–2000 ms
- Reset nur per „Schutz zurücksetzen"; Software-Überwachung ist polling-begrenzt und ersetzt keine Hardware-Sicherung

## Bedienung
- Sollwerte: SpinBox + Slider (0–30 V / 0–10 A, geklemmt), „Setzen", optional Live-Übernahme beim Loslassen
- Ausgang: großer Toggle, Bestätigung bei Sollspannung > 12 V
- Messung: große Ziffern V/A/W, CV/CC-Hinweis, Live-Plot (V links, A rechts, Fenster 10 s–30 min, Schwellenlinien, Trip-Marker)
- Sonstiges: Polling 100–2000 ms, Remote/Local, Raw-SCPI Send/Query, Log, CSV-Aufzeichnung (`timestamp,volt,ampere,watt`)

## Struktur
- `owon_spe3103/scpi_map.py` — einziger Ort für SCPI-Strings
- `driver.py` Worker-Thread/Queue/Polling · `discovery.py` Befehlserkennung · `protection.py` OVP/OCP · `gui.py` Fenster · `plot.py` Live-Plot

## Hinweise
- Bei Disconnect und Programmende: Ausgang aus → Local → Verbindung schließen
- SCPI-Kandidaten sind unverifiziert; Discovery entscheidet zur Laufzeit
