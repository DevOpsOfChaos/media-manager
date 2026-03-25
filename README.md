# Media Manager

Saubere Python-Basis für einen öffentlichen Foto- und Medienmanager.

Der aktuelle Stand ist bewusst fokussiert:
- Medien per Metadaten analysieren
- Bilder und Videos nach Datum in Zielordner sortieren
- sichere Vorschau per Dry-Run als Standard
- modularer Aufbau für spätere Features wie Umbenennen, Duplikaterkennung und Video-Analyse

## Bereits enthalten

- CLI mit `organize`-Befehl
- ExifTool-Erkennung über PATH, Umgebungsvariable oder expliziten Pfad
- Datumswahl über priorisierte Metadaten-Tags
- Fallback auf Dateisystem-Zeitstempel
- konfigurierbares Zielpfad-Template
- Kollisionserkennung bei Dateinamen
- Unit-Tests für Datumsparser und Zielpfadaufbau

## Noch nicht enthalten

- intelligentes Umbenennen nach Vorlage
- echte Duplikaterkennung über Hashing/Perceptual Hash
- Video-Frame-Analyse
- GUI/Weboberfläche
- Datenbankindex für große Bibliotheken

## Projektstruktur

```text
media-manager/
├── docs/
├── src/
│   └── media_manager/
├── tests/
├── .gitignore
├── pyproject.toml
└── README.md
```

## Voraussetzungen

- Python 3.11+
- [ExifTool](https://exiftool.org/) installiert
- Windows PowerShell oder Terminal

## Installation

### 1. Repository anlegen

```powershell
mkdir C:\Users\mries\Documents\LocalRepos\media-manager
cd C:\Users\mries\Documents\LocalRepos\media-manager
```

### 2. Dateien aus dem ZIP entpacken

Das ZIP in diesen Ordner entpacken.

### 3. Virtuelle Umgebung anlegen

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e .
```

### 4. ExifTool prüfen

Variante A: ExifTool liegt im PATH.

```powershell
exiftool -ver
```

Variante B: Pfad per Umgebungsvariable setzen.

```powershell
$env:EXIFTOOL_PATH = 'C:\Program Files\exiftool\exiftool.exe'
```

## Verwendung

### Sicherer Testlauf

```powershell
python -m media_manager organize "D:\Fotos\Unsortiert" "D:\Fotos\Sortiert"
```

Standard ist Dry-Run. Es wird also nur angezeigt, was passieren würde.

### Wirklich kopieren

```powershell
python -m media_manager organize "D:\Fotos\Unsortiert" "D:\Fotos\Sortiert" --apply --copy
```

### Wirklich verschieben

```powershell
python -m media_manager organize "D:\Fotos\Unsortiert" "D:\Fotos\Sortiert" --apply --move
```

### Eigenes Ordner-Template

```powershell
python -m media_manager organize "D:\Fotos\Unsortiert" "D:\Fotos\Sortiert" --apply --copy --template "{year}/{month_num}-{month_name}/{day}"
```

Verfügbare Platzhalter:

- `{year}`
- `{month_num}`
- `{month_name}`
- `{day}`
- `{hour}`
- `{minute}`
- `{ext}`

## Tests

```powershell
pytest
```

## Git-Start

```powershell
git init
git branch -M main
git add .
git commit -m "chore: initial public media manager foundation"
```

## Ehrliche Einschätzung

Dein ursprüngliches Skript war ein brauchbarer Start, aber als öffentliches Projekt zu roh. Die Kernprobleme waren ein hart kodierter ExifTool-Pfad, eine monolithische Struktur und fehlende Sicherheitsmechanismen für destructive operations. Diese Basis behebt genau das und verschiebt die Komplexität dorthin, wo sie hingehört: in saubere Module.
