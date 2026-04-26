from __future__ import annotations

from collections.abc import Mapping
from typing import Any

LANGUAGE_SCHEMA_VERSION = "1.0"
DEFAULT_LANGUAGE = "en"
SUPPORTED_LANGUAGES = ("en", "de")

_TRANSLATIONS: dict[str, dict[str, str]] = {
    "en": {
        "app.title": "Media Manager",
        "app.subtitle": "Organize, review, and curate your local media library.",
        "nav.dashboard": "Dashboard",
        "nav.new-run": "New run",
        "nav.people-review": "People review",
        "nav.run-history": "Run history",
        "nav.profiles": "Profiles",
        "nav.settings": "Settings",
        "page.dashboard.title": "Dashboard",
        "page.dashboard.description": "Your media workflows at a glance.",
        "page.new-run.title": "New run",
        "page.new-run.description": "Create a safe preview before changing files.",
        "page.people-review.title": "People review",
        "page.people-review.description": "Confirm people groups, reject wrong faces, and train your local catalog.",
        "page.run-history.title": "Run history",
        "page.run-history.description": "Inspect previous previews and apply runs.",
        "page.profiles.title": "Profiles",
        "page.profiles.description": "Saved workflow presets for repeatable tasks.",
        "page.settings.title": "Settings / Doctor",
        "page.settings.description": "Language, appearance, diagnostics, and privacy settings.",
        "dashboard.profiles": "Profiles",
        "dashboard.runs": "Recent runs",
        "dashboard.people": "People review",
        "dashboard.ready": "Ready",
        "action.open": "Open",
        "action.review": "Review",
        "action.preview": "Preview",
        "action.apply": "Apply after review",
        "action.settings": "Settings",
        "status.ready": "Ready.",
        "status.missing_qt": "PySide6 is not installed. Install the GUI extra to launch the modern desktop app.",
        "privacy.people": "People data stays local. Face crops and embeddings are sensitive biometric metadata.",
        "onboarding.title": "Welcome to Media Manager",
        "onboarding.step1": "Start with a preview. The app should not change files until you explicitly apply.",
        "onboarding.step2": "Review warnings and people groups before training or applying changes.",
        "onboarding.step3": "Keep people catalogs, face crops, and reports private.",
        "settings.language": "Language",
        "settings.theme": "Theme",
        "settings.privacy": "Privacy",
        "theme.modern_dark": "Modern dark",
        "theme.modern_light": "Modern light",
        "theme.system": "System",
        "people.empty": "Open or create a people review bundle.",
        "people.ready_groups": "Ready groups",
        "people.needs_review": "Needs review",
        "people.needs_name": "Needs name",
        "people.faces": "Faces",
        "people.groups": "Groups",
        "command_palette.title": "Command palette",
        "command.open_people_review": "Open people review",
        "command.new_people_scan": "New people scan",
        "command.open_profiles": "Open profiles",
        "command.open_runs": "Open run history",
    },
    "de": {
        "app.title": "Media Manager",
        "app.subtitle": "Lokale Medien organisieren, prüfen und kuratieren.",
        "nav.dashboard": "Übersicht",
        "nav.new-run": "Neuer Lauf",
        "nav.people-review": "Personenprüfung",
        "nav.run-history": "Laufhistorie",
        "nav.profiles": "Profile",
        "nav.settings": "Einstellungen",
        "page.dashboard.title": "Übersicht",
        "page.dashboard.description": "Deine Medien-Workflows auf einen Blick.",
        "page.new-run.title": "Neuer Lauf",
        "page.new-run.description": "Erstelle zuerst eine sichere Vorschau, bevor Dateien geändert werden.",
        "page.people-review.title": "Personenprüfung",
        "page.people-review.description": "Personengruppen bestätigen, falsche Gesichter ablehnen und den lokalen Katalog trainieren.",
        "page.run-history.title": "Laufhistorie",
        "page.run-history.description": "Frühere Vorschauen und Apply-Läufe prüfen.",
        "page.profiles.title": "Profile",
        "page.profiles.description": "Gespeicherte Workflow-Voreinstellungen für wiederholbare Aufgaben.",
        "page.settings.title": "Einstellungen / Doctor",
        "page.settings.description": "Sprache, Darstellung, Diagnose und Datenschutz.",
        "dashboard.profiles": "Profile",
        "dashboard.runs": "Letzte Läufe",
        "dashboard.people": "Personenprüfung",
        "dashboard.ready": "Bereit",
        "action.open": "Öffnen",
        "action.review": "Prüfen",
        "action.preview": "Vorschau",
        "action.apply": "Nach Prüfung anwenden",
        "action.settings": "Einstellungen",
        "status.ready": "Bereit.",
        "status.missing_qt": "PySide6 ist nicht installiert. Installiere das GUI-Extra, um die moderne Desktop-App zu starten.",
        "privacy.people": "Personendaten bleiben lokal. Face-Crops und Embeddings sind sensible biometrische Metadaten.",
        "onboarding.title": "Willkommen im Media Manager",
        "onboarding.step1": "Beginne mit einer Vorschau. Die App soll Dateien erst nach ausdrücklicher Bestätigung ändern.",
        "onboarding.step2": "Prüfe Warnungen und Personengruppen, bevor trainiert oder angewendet wird.",
        "onboarding.step3": "Halte Personen-Kataloge, Face-Crops und Reports privat.",
        "settings.language": "Sprache",
        "settings.theme": "Darstellung",
        "settings.privacy": "Datenschutz",
        "theme.modern_dark": "Modern dunkel",
        "theme.modern_light": "Modern hell",
        "theme.system": "System",
        "people.empty": "Öffne oder erstelle ein Personenprüfungs-Bundle.",
        "people.ready_groups": "Bereite Gruppen",
        "people.needs_review": "Zu prüfen",
        "people.needs_name": "Name fehlt",
        "people.faces": "Gesichter",
        "people.groups": "Gruppen",
        "command_palette.title": "Befehlspalette",
        "command.open_people_review": "Personenprüfung öffnen",
        "command.new_people_scan": "Neuen Personen-Scan starten",
        "command.open_profiles": "Profile öffnen",
        "command.open_runs": "Laufhistorie öffnen",
    },
}


def normalize_language(language: str | None) -> str:
    value = str(language or DEFAULT_LANGUAGE).strip().lower().replace("_", "-")
    if value.startswith("de"):
        return "de"
    if value.startswith("en"):
        return "en"
    return DEFAULT_LANGUAGE


def translate(key: str, *, language: str | None = None, fallback: str | None = None) -> str:
    lang = normalize_language(language)
    return _TRANSLATIONS.get(lang, {}).get(key) or _TRANSLATIONS[DEFAULT_LANGUAGE].get(key) or fallback or key


def translate_many(keys: list[str] | tuple[str, ...], *, language: str | None = None) -> dict[str, str]:
    return {key: translate(key, language=language) for key in keys}


def localize_navigation_item(item: Mapping[str, Any], *, language: str | None = None) -> dict[str, object]:
    page_id = str(item.get("id") or item.get("page_id") or "").strip()
    payload = dict(item)
    if page_id:
        payload["label"] = translate(f"nav.{page_id}", language=language, fallback=str(item.get("label") or page_id))
    return payload


def build_language_catalog(language: str | None = None) -> dict[str, object]:
    lang = normalize_language(language)
    return {
        "schema_version": LANGUAGE_SCHEMA_VERSION,
        "language": lang,
        "supported_languages": list(SUPPORTED_LANGUAGES),
        "labels": dict(_TRANSLATIONS[lang]),
        "fallback_language": DEFAULT_LANGUAGE,
    }


__all__ = [
    "DEFAULT_LANGUAGE",
    "LANGUAGE_SCHEMA_VERSION",
    "SUPPORTED_LANGUAGES",
    "build_language_catalog",
    "localize_navigation_item",
    "normalize_language",
    "translate",
    "translate_many",
]
