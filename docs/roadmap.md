# Roadmap

## Phase 1 – solide CLI-Basis

- [x] Medien nach Datum sortieren
- [x] Dry-Run als Standard
- [x] ExifTool sauber integrieren
- [x] Tests für Kernlogik

## Phase 2 – produktiv brauchbar

- [ ] Umbenennen nach Vorlagen wie `{date}_{camera}_{sequence}`
- [ ] konfigurierbare Regeln per JSON oder YAML
- [ ] Hash-basierte Duplikaterkennung
- [ ] Erkennung ähnlicher Bilder
- [ ] Export eines Prüfberichts

## Phase 3 – echter Media Manager

- [ ] Bibliotheksindex mit SQLite
- [ ] Vorschaubilder und Metadaten-Cache
- [ ] Video-Metadaten und Frame-Scans
- [ ] Such- und Filterfunktionen
- [ ] Weboberfläche
- [ ] GitHub Actions für Tests und Linting

## Strategische Priorität

Nicht sofort eine GUI bauen. Das ist typischer Anfängerfehler. Erst muss die Kernlogik stabil, testbar und dateisicher sein. Sonst baust du nur eine hübsche Oberfläche über unzuverlässigen Dateischrott.
