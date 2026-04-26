from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

VIEW_PREFS_SCHEMA_VERSION = "1.0"
_ALLOWED_DENSITIES = {"compact", "comfortable", "spacious"}
_ALLOWED_LANGUAGES = {"en", "de"}
_ALLOWED_THEMES = {"modern-dark", "modern-light", "system"}


def normalize_view_preferences(payload: Mapping[str, Any] | None = None, **overrides: Any) -> dict[str, object]:
    data = dict(payload or {})
    data.update({key: value for key, value in overrides.items() if value is not None})
    language = str(data.get("language") or "en").lower()
    if language not in _ALLOWED_LANGUAGES:
        language = "en"
    theme = str(data.get("theme") or "modern-dark").replace("_", "-")
    if theme not in _ALLOWED_THEMES:
        theme = "modern-dark"
    density = str(data.get("density") or "comfortable").lower()
    if density not in _ALLOWED_DENSITIES:
        density = "comfortable"
    return {
        "schema_version": VIEW_PREFS_SCHEMA_VERSION,
        "kind": "view_preferences",
        "language": language,
        "theme": theme,
        "density": density,
        "start_page_id": str(data.get("start_page_id") or "dashboard"),
        "show_onboarding": bool(data.get("show_onboarding", True)),
        "remember_recent_paths": bool(data.get("remember_recent_paths", True)),
    }


def load_view_preferences(path: str | Path | None) -> dict[str, object]:
    if path is None or not Path(path).exists():
        return normalize_view_preferences()
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return normalize_view_preferences(payload if isinstance(payload, dict) else {})


def save_view_preferences(path: str | Path, preferences: Mapping[str, Any]) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(normalize_view_preferences(preferences), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return output


__all__ = ["VIEW_PREFS_SCHEMA_VERSION", "normalize_view_preferences", "load_view_preferences", "save_view_preferences"]
