# OWON SPE3103 GUI

Ein Bedienprogramm für mein OWON SPE3103 Labornetzteil (30 V / 10 A, ein Kanal). Windows-Desktop, Python, PyQt6.
Entstanden, weil ich Messreihen mitschreiben und den Ausgang bei Überspannung sicher abschalten wollte, ohne dabei am Gerät zu stehen.

## Was es kann

- Spannung und Strom setzen, per Zahlenfeld oder Schieberegler
- Ausgang ein/aus mit großem Toggle, Rückfrage wenn die Sollspannung über 12 V liegt
- Messwerte V / A / W groß ablesbar, dazu ein Live-Plot mit zwei Y-Achsen
- OVP/OCP: Schwellen setzen, bei Auslösung schaltet der Ausgang ab und ein roter Banner sagt warum
- Mitschreiben als CSV (`timestamp,volt,ampere,watt`)
- Rohes SCPI senden und abfragen, dazu ein Log das jeden Ein- und Ausgang zeigt

## Installation

Getestet mit Python 3.11 und 3.12 unter Windows 11.

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

NI-VISA wird nicht gebraucht, das Backend ist `pyvisa-py`. Das SPE3103 meldet sich bei mir als serieller Port,
also läuft die Kommunikation über pyserial (`ASRL3::INSTR` o.ä.). Je nach Firmware kann es auch als USBTMC auftauchen —
in dem Fall steht es einfach mit einer anderen Adresse in der Auswahlliste.

## Loslegen

```
python main.py
```

Ressource aus der Liste wählen (oder von Hand eintippen), Baudrate prüfen, Connect. Der Ausgang bleibt beim Verbinden aus,
das ist Absicht und wird auch so bleiben.

Zum Ausprobieren ohne Hardware:

```
python main.py --demo
```

Das simulierte Gerät liefert leicht schwankende Werte und hat zwei Knöpfe, mit denen sich OVP und OCP absichtlich
auslösen lassen — damit lässt sich die Schutzlogik testen, ohne ein echtes Netzteil zu quälen.

## Als exe

Wer keine Python-Umgebung aufsetzen will, baut sich eine einzelne Datei:

```
pip install pyinstaller
pyinstaller --onefile --windowed --name OWON-SPE3103 --hidden-import pyvisa_py --collect-submodules pyvisa_py main.py
```

Danach liegt `OWON-SPE3103.exe` in `dist/` (~50 MB, weil Qt komplett mit drin steckt). Der Ordner ist bewusst
nicht im Repo. Das Profil `scpi_profile.json` legt die exe neben sich selbst ab, sie sollte also in einem
Ordner liegen wo sie schreiben darf.

## Warum die SCPI-Befehle gesucht werden

Für das SPE3103 lag mir keine belastbare Befehlsreferenz vor, und geraten wollte ich nicht. Deshalb steht in
`scpi_map.py` pro Funktion eine Liste plausibler Kandidaten, und beim ersten Verbinden probiert `discovery.py` sie durch:
Abfragen direkt, schreibende Befehle nur bei ausgeschaltetem Ausgang und mit Readback, danach jeweils `SYST:ERR?`
um zu sehen ob das Gerät den Befehl geschluckt hat.

Was funktioniert hat, landet in `scpi_profile.json` neben der `main.py` und wird beim nächsten Start wiederverwendet.
Löschen der Datei erzwingt einen neuen Durchlauf. Alles was sich nicht auflösen ließ, steht im GUI als
„nicht unterstützt" an der jeweiligen Bedienung — lieber ein graues Feld als ein Knopf, der nichts tut.

Sämtliche SCPI-Strings stehen ausschließlich in `scpi_map.py`. Wenn du eine verifizierte Befehlsliste für dein
Gerät hast: dort eintragen, sonst nirgends.

## Schutz, zweistufig

Zuerst der Schutz im Gerät selbst, falls die Discovery die passenden Befehle findet: Schwelle setzen, aktivieren,
und im selben Poll-Zyklus wie die Messwerte den Trip-Status abfragen.

Unabhängig davon läuft immer eine Software-Überwachung mit. Sie vergleicht jeden Messwert gegen die Schwellen und
schickt bei Überschreitung sofort ein Abschaltkommando, das sich in der Queue vordrängelt. Die Ansprechverzögerung
(0–2000 ms, standardmäßig 0) hilft gegen Fehlauslösungen durch Einschaltspitzen.

Zurückgesetzt wird nur von Hand über „Schutz zurücksetzen". Kein Auto-Reset — wenn etwas ausgelöst hat, will ich
wissen warum, bevor wieder Spannung anliegt.

**Wichtig:** die Software-Stufe kann nur so schnell reagieren wie das Polling-Intervall es zulässt (100–2000 ms).
Das ist eine Komfortfunktion und ersetzt keine Sicherung und keinen echten Hardware-Schutz. Wer empfindliche
Schaltungen aufbaut, sollte sich nicht darauf verlassen.

## Aufbau

```
main.py                  Start, --demo Schalter
owon_spe3103/
  scpi_map.py            alle SCPI-Strings, Kandidatenlisten, Gerätegrenzen
  driver.py              PyVISA im eigenen Thread, Queue, Polling, Reconnect
  discovery.py           Befehlserkennung und Profil-Cache
  protection.py          OVP/OCP, Schwellen und Software-Überwachung
  gui.py                 Fenster und Bedienung
  plot.py                Live-Plot
```

Der GUI-Thread fasst PyVISA nie direkt an. Alles läuft über eine Queue in den Worker-Thread, mit einem
Prioritätsslot fürs Abschalten. Der Plot hält seine Daten in `deque`s mit fester Obergrenze, damit er auch nach
Stunden bei 250 ms Takt nicht den Speicher vollschreibt.

## Bekannte Ecken

- Die CV/CC-Anzeige ist geraten (Messstrom gegen Sollstrom), nicht vom Gerät gemeldet
- Bei Verbindungsabbruch versucht der Treiber dreimal zu reconnecten und gibt dann auf
- Die Kandidatenlisten sind auf meinem Gerät gewachsen; auf anderer Firmware kann mehr oder weniger davon durchfallen

## Sicherheit

Sollwerte werden vor dem Senden auf 0–30 V / 0–10 A geklemmt, Schutzschwellen auf 0–33 V / 0–11 A. Beim Trennen und
beim Beenden geht erst der Ausgang aus, dann zurück auf lokale Bedienung, dann wird die Verbindung geschlossen.

Trotzdem: das ist ein Hobbyprojekt an einem Netzteil, das reale Schaltungen kaputt machen kann. Nutzung auf eigenes Risiko.
