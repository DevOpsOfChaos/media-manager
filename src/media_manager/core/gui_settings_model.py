from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

from .app_services import read_json_object, write_json_object
from .gui_i18n import DEFAULT_LANGUAGE, normalize_language
from .gui_layout import DEFAULT_DENSITY, normalize_density
from .gui_theme import DEFAULT_THEME, normalize_theme

SETTINGS_SCHEMA_VERSION = "1.1"


def default_gui_settings() -> dict[str, object]:
    return {
        "schema_version": SETTINGS_SCHEMA_VERSION,
        "language": DEFAULT_LANGUAGE,
        "theme": DEFAULT_THEME,
        "density": DEFAULT_DENSITY,
        "start_page_id": "dashboard",
        "confirm_before_apply": True,
        "people_privacy_acknowledged": False,
        "show_onboarding": True,
        "enable_command_palette": True,
        "recent_paths": {
            "profile_dir": None,
            "run_dir": None,
            "people_bundle_dir": None,
            "catalog": None,
        },
        "window": {
            "width": 1400,
            "height": 900,
            "maximized": False,
        },
    }


def normalize_gui_settings(payload: Mapping[str, Any] | None = None) -> dict[str, object]:
    base = default_gui_settings()
    value = dict(payload or {})
    recent = value.get("recent_paths") if isinstance(value.get("recent_paths"), Mapping) else {}
    window = value.get("window") if isinstance(value.get("window"), Mapping) else {}
    return {
        **base,
        **value,
        "schema_version": SETTINGS_SCHEMA_VERSION,
        "language": normalize_language(str(value.get("language", base["language"]))),
        "theme": normalize_theme(str(value.get("theme", base["theme"]))),
        "density": normalize_density(str(value.get("density", base["density"]))),
        "start_page_id": str(value.get("start_page_id") or base["start_page_id"]),
        "confirm_before_apply": bool(value.get("confirm_before_apply", True)),
        "people_privacy_acknowledged": bool(value.get("people_privacy_acknowledged", False)),
        "show_onboarding": bool(value.get("show_onboarding", True)),
        "enable_command_palette": bool(value.get("enable_command_palette", True)),
        "recent_paths": {**base["recent_paths"], **dict(recent)},
        "window": {**base["window"], **dict(window)},
    }


def load_gui_settings(path: str | Path | None) -> dict[str, object]:
    if path is None:
        return default_gui_settings()
    resolved = Path(path)
    if not resolved.exists():
        return default_gui_settings()
    return normalize_gui_settings(read_json_object(resolved))


def write_gui_settings(path: str | Path, settings: Mapping[str, Any]) -> Path:
    return write_json_object(path, normalize_gui_settings(settings))


def update_gui_settings(settings: Mapping[str, Any], **updates: object) -> dict[str, object]:
    current = normalize_gui_settings(settings)
    recent_updates = updates.pop("recent_paths", None)
    window_updates = updates.pop("window", None)
    if isinstance(recent_updates, Mapping):
        current["recent_paths"] = {**dict(current.get("recent_paths", {})), **dict(recent_updates)}
    if isinstance(window_updates, Mapping):
        current["window"] = {**dict(current.get("window", {})), **dict(window_updates)}
    current.update({key: value for key, value in updates.items() if value is not None})
    return normalize_gui_settings(current)


__all__ = [
    "SETTINGS_SCHEMA_VERSION",
    "default_gui_settings",
    "load_gui_settings",
    "normalize_gui_settings",
    "update_gui_settings",
    "write_gui_settings",
]
