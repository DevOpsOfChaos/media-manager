from __future__ import annotations

QT_RUNTIME_SMOKE_DESKTOP_OPERATOR_NOTES_SCHEMA_VERSION = "1.0"

def build_qt_runtime_smoke_desktop_operator_notes(*, language: str = "de") -> dict[str, object]:
    lang = "de" if language == "de" else "en"
    notes = [
        {"id": "manual-only", "text": "Start the desktop UI manually; no command is executed by this plan." if lang == "en" else "Starte die Desktop-UI manuell; dieser Plan führt keinen Befehl aus."},
        {"id": "local-only", "text": "Keep People Review data local; do not upload screenshots with faces." if lang == "en" else "People-Review-Daten lokal halten; keine Screenshots mit Gesichtern hochladen."},
        {"id": "no-training", "text": "No apply/training action should start automatically." if lang == "en" else "Keine Apply-/Training-Aktion darf automatisch starten."},
    ]
    return {
        "schema_version": QT_RUNTIME_SMOKE_OPERATOR_NOTES_SCHEMA_VERSION if False else QT_RUNTIME_SMOKE_DESKTOP_OPERATOR_NOTES_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_desktop_operator_notes",
        "language": lang,
        "notes": notes,
        "summary": {"note_count": len(notes), "opens_window": False, "executes_commands": False, "local_only": True},
        "capabilities": {"requires_pyside6": False, "opens_window": False, "headless_testable": True, "executes_commands": False, "local_only": True},
    }

__all__ = ["QT_RUNTIME_SMOKE_DESKTOP_OPERATOR_NOTES_SCHEMA_VERSION", "build_qt_runtime_smoke_desktop_operator_notes"]
