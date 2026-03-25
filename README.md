# Media Manager

Solide Desktop-Basis für einen später öffentlich nutzbaren Foto- und Medienmanager.

Der Stand ist absichtlich pragmatisch:
- bewährte Kernlogik für Medien-Sortierung beibehalten
- Desktop-Oberfläche mit Tkinter für sofort nutzbare Bedienung
- CLI bleibt erhalten
- Architektur bleibt so getrennt, dass später eine moderne Oberfläche darauf aufsetzen kann

## Was bereits funktioniert

- Fotos und Videos per Metadaten nach Datum sortieren
- Vorschau ohne Änderungen
- echtes Kopieren oder Verschieben
- ExifTool-Erkennung über PATH, Umgebungsvariable oder expliziten Pfad
- Fallback auf Dateisystem-Zeitstempel
- Kollisionserkennung bei Dateinamen
- Desktop-GUI mit Ordnerauswahl und Ergebnisliste
- Tests für Datumsparser und Sortierlogik

## Was bewusst noch fehlt

- Umbenennen nach Vorlage
- Duplikaterkennung
- Datenbankindex
- Video-Inhaltsanalyse
- moderne professionelle UI
- Installer/Setup-Paket

## Architektur

```text
media-manager/
├── docs/
├── src/
│   └── media_manager/
│       ├── cli.py
│       ├── gui.py
│       ├── sorter.py
│       ├── exiftool.py
│       └── dates.py
├── tests/
├── pyproject.toml
└── README.md
```

Die Logik ist absichtlich **nicht** in die GUI eingebrannt. Das ist wichtig, weil Tkinter nur die Startbasis ist.
Wenn du später auf **PySide6** wechselst, bleibt die Kernlogik nutzbar.

## Voraussetzungen

- Windows
- Python 3.11+
- ExifTool

## Saubere Einschätzung zu deinem bisherigen Stand

Dein altes Skript war nicht das Problem. Die Kernlogik scheint bereits gut zu funktionieren.
Das eigentliche Defizit lag bei Projektstruktur, Setup, Fehlerbehandlung und fehlender Oberfläche.
Genau das behebt diese Basis.

## Installation auf deinem Windows-Rechner

Du hast bereits gezeigt, dass `python` bei dir funktioniert.
Also **nicht weiter Zeit mit `py -3.11` verschwenden**, solange dein Launcher nicht sauber eingerichtet ist.

### 1. In den Projektordner wechseln

```powershell
cd C:\Users\mries\Documents\LocalRepos\media-manager
```

### 2. ZIP hier entpacken

Danach sollten `README.md`, `pyproject.toml`, `src`, `tests` direkt in diesem Ordner liegen.

### 3. Virtuelle Umgebung anlegen

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

Falls `Activate.ps1` wegen der Execution Policy blockiert wird:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### 4. ExifTool installieren

ExifTool muss real vorhanden sein. Eine Umgebungsvariable auf einen nicht existierenden Pfad zu setzen bringt gar nichts.

Danach entweder:

```powershell
exiftool -ver
```

oder explizit in der GUI/CLI den Pfad setzen, z. B.:

```powershell
$env:EXIFTOOL_PATH = "C:\Tools\ExifTool\exiftool.exe"
```

## GUI starten

```powershell
python -m media_manager
```

oder:

```powershell
media-manager-gui
```

## CLI weiter benutzen

Vorschau:

```powershell
python -m media_manager organize "C:\Pfad\Zu\Unsortiert" "C:\Pfad\Zu\Sortiert"
```

Wirklich kopieren:

```powershell
python -m media_manager organize "C:\Pfad\Zu\Unsortiert" "C:\Pfad\Zu\Sortiert" --apply --copy
```

Wirklich verschieben:

```powershell
python -m media_manager organize "C:\Pfad\Zu\Unsortiert" "C:\Pfad\Zu\Sortiert" --apply --move
```

## Wichtige Korrektur zu deinem letzten Versuch

Drei Dinge waren bei deinem Test kein echter Programmfehler:

1. `py -3.11` schlug fehl, weil dein Python-Launcher nicht passend eingerichtet ist.
   Das heißt nicht, dass Python fehlt.
2. `D:\Fotos\Unsortiert` war nur ein Beispielpfad. Wenn der Ordner nicht existiert, **muss** das Programm abbrechen.
3. `https://github.com/DEINNAME/media-manager.git` war ein Platzhalter. Natürlich kann man darauf nicht pushen.

## Tests

```powershell
pytest
```

## Git-Start

```powershell
git add .
git commit -m "feat: add desktop gui foundation for media manager"
```

## Strategisch richtiger nächster Schritt

Nicht sofort in zehn Features verzetteln.

Diese Reihenfolge ist sinnvoll:
1. GUI-Basis stabilisieren
2. Umbenennen nach Vorlage ergänzen
3. Duplikaterkennung ergänzen
4. Bibliotheksindex auf SQLite-Basis einführen
5. erst dann moderne UI mit PySide6 oder Web-Frontend evaluieren


## Windows-Hinweise

- Alter bekannter ExifTool-Standardpfad aus dem Ursprungsskript:
  `C:\Program Files\exiftool\exiftool.exe`
- Fallback aus dem Ursprungsskript:
  `C:\Program Files\exiftool\exiftool(-k).exe`
- Wenn `python -m media_manager` mit `No module named tkinter` endet, enthält deine aktuelle Python-Installation kein Tkinter. Die CLI funktioniert dann trotzdem weiter.
