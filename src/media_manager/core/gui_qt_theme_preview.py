from __future__ import annotations

from collections.abc import Mapping
from typing import Any

THEME_PREVIEW_SCHEMA_VERSION = "1.0"


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def build_theme_preview(theme_payload: Mapping[str, Any]) -> dict[str, object]:
    palette = _mapping(theme_payload.get("palette") or theme_payload.get("tokens"))
    chips = []
    for key in ("background", "surface", "text", "muted", "accent", "success", "warning", "danger"):
        if key in palette:
            chips.append({"id": key, "label": key.replace("_", " ").title(), "value": palette[key]})
    return {
        "schema_version": THEME_PREVIEW_SCHEMA_VERSION,
        "kind": "qt_theme_preview",
        "theme": theme_payload.get("theme", "modern-dark"),
        "chip_count": len(chips),
        "chips": chips,
        "sample_cards": [
            {"id": "primary", "title": "Primary card", "accent": palette.get("accent")},
            {"id": "warning", "title": "Warning state", "accent": palette.get("warning")},
        ],
        "has_required_colors": all(key in palette for key in ("background", "surface", "text", "accent")),
    }


__all__ = ["THEME_PREVIEW_SCHEMA_VERSION", "build_theme_preview"]
