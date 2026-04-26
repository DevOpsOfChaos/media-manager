from __future__ import annotations

from collections.abc import Mapping
from typing import Any

SETTINGS_BINDER_SCHEMA_VERSION = "1.0"

ALLOWED_LANGUAGES = ("en", "de")
ALLOWED_THEMES = ("modern-dark", "modern-light", "system")
ALLOWED_DENSITIES = ("compact", "comfortable", "spacious")


def _text(value: object, fallback: str = "") -> str:
    return str(value) if value is not None else fallback


def build_qt_settings_form(settings: Mapping[str, Any] | None = None) -> dict[str, object]:
    settings = settings or {}
    return {
        "schema_version": SETTINGS_BINDER_SCHEMA_VERSION,
        "kind": "qt_settings_form",
        "fields": [
            {"id": "language", "label": "Language", "type": "choice", "choices": list(ALLOWED_LANGUAGES), "value": _text(settings.get("language"), "en")},
            {"id": "theme", "label": "Theme", "type": "choice", "choices": list(ALLOWED_THEMES), "value": _text(settings.get("theme"), "modern-dark")},
            {"id": "density", "label": "Density", "type": "choice", "choices": list(ALLOWED_DENSITIES), "value": _text(settings.get("density"), "comfortable")},
            {"id": "show_onboarding", "label": "Show onboarding", "type": "boolean", "value": bool(settings.get("show_onboarding", True))},
            {"id": "people_privacy_acknowledged", "label": "People privacy acknowledged", "type": "boolean", "value": bool(settings.get("people_privacy_acknowledged", False))},
        ],
    }


def build_settings_update_intent(field_id: str, value: object) -> dict[str, object]:
    return {
        "schema_version": SETTINGS_BINDER_SCHEMA_VERSION,
        "kind": "settings_update_intent",
        "field_id": str(field_id),
        "value": value,
        "executes_immediately": False,
        "requires_save": True,
    }


__all__ = ["SETTINGS_BINDER_SCHEMA_VERSION", "build_qt_settings_form", "build_settings_update_intent"]
