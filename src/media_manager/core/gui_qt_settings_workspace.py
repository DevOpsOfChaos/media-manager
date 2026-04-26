from __future__ import annotations

from collections.abc import Mapping
from typing import Any

SETTINGS_WORKSPACE_SCHEMA_VERSION = "1.0"

_SUPPORTED_LANGUAGES = {"en", "de"}
_SUPPORTED_THEMES = {"modern-dark", "modern-light", "system"}
_SUPPORTED_DENSITIES = {"compact", "comfortable", "spacious"}


def normalize_settings_workspace(values: Mapping[str, Any] | None = None) -> dict[str, object]:
    values = values or {}
    language = str(values.get("language") or "en").lower()
    theme = str(values.get("theme") or "modern-dark").lower()
    density = str(values.get("density") or "comfortable").lower()
    return {
        "schema_version": SETTINGS_WORKSPACE_SCHEMA_VERSION,
        "language": language if language in _SUPPORTED_LANGUAGES else "en",
        "theme": theme if theme in _SUPPORTED_THEMES else "modern-dark",
        "density": density if density in _SUPPORTED_DENSITIES else "comfortable",
        "start_page_id": str(values.get("start_page_id") or "dashboard"),
        "people_privacy_acknowledged": bool(values.get("people_privacy_acknowledged", False)),
    }


def build_settings_workspace(values: Mapping[str, Any] | None = None) -> dict[str, object]:
    settings = normalize_settings_workspace(values)
    fields = [
        {"id": "language", "label": "Language", "type": "select", "choices": sorted(_SUPPORTED_LANGUAGES), "value": settings["language"]},
        {"id": "theme", "label": "Theme", "type": "select", "choices": sorted(_SUPPORTED_THEMES), "value": settings["theme"]},
        {"id": "density", "label": "Density", "type": "select", "choices": sorted(_SUPPORTED_DENSITIES), "value": settings["density"]},
        {"id": "start_page_id", "label": "Start page", "type": "text", "value": settings["start_page_id"]},
        {"id": "people_privacy_acknowledged", "label": "People privacy acknowledged", "type": "checkbox", "value": settings["people_privacy_acknowledged"], "sensitive": True},
    ]
    return {
        "schema_version": SETTINGS_WORKSPACE_SCHEMA_VERSION,
        "kind": "settings_workspace",
        "settings": settings,
        "sections": [{"id": "appearance", "title": "Appearance", "fields": fields[:3]}, {"id": "startup_privacy", "title": "Startup & Privacy", "fields": fields[3:]}],
        "field_count": len(fields),
        "sensitive_field_count": sum(1 for field in fields if field.get("sensitive")),
    }


def validate_settings_workspace(workspace: Mapping[str, Any]) -> dict[str, object]:
    settings = workspace.get("settings") if isinstance(workspace.get("settings"), Mapping) else workspace
    normalized = normalize_settings_workspace(settings)
    warnings: list[str] = []
    if not normalized["people_privacy_acknowledged"]:
        warnings.append("people_privacy_not_acknowledged")
    return {
        "schema_version": SETTINGS_WORKSPACE_SCHEMA_VERSION,
        "valid": True,
        "warning_count": len(warnings),
        "warnings": warnings,
        "normalized": normalized,
    }


__all__ = ["SETTINGS_WORKSPACE_SCHEMA_VERSION", "build_settings_workspace", "normalize_settings_workspace", "validate_settings_workspace"]
