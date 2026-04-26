from __future__ import annotations

from collections.abc import Mapping
from typing import Any

LOCALIZATION_SURFACE_SCHEMA_VERSION = "1.0"


def _walk_strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, Mapping):
        result: list[str] = []
        for item in value.values():
            result.extend(_walk_strings(item))
        return result
    if isinstance(value, list):
        result: list[str] = []
        for item in value:
            result.extend(_walk_strings(item))
        return result
    return []


def build_localization_surface(model: Mapping[str, Any], *, language: str = "de") -> dict[str, object]:
    strings = _walk_strings(model)
    english_markers = ["Open ", "Review ", "Settings", "Dashboard", "People review"]
    possible_english = sorted({text for text in strings if any(marker in text for marker in english_markers)})
    return {
        "schema_version": LOCALIZATION_SURFACE_SCHEMA_VERSION,
        "kind": "localization_surface",
        "language": language,
        "string_count": len(strings),
        "possible_english_count": len(possible_english) if language == "de" else 0,
        "possible_english": possible_english if language == "de" else [],
        "coverage_hint": "review" if language == "de" and possible_english else "ok",
    }


def merge_localization_surfaces(*surfaces: Mapping[str, Any]) -> dict[str, object]:
    possible: set[str] = set()
    total = 0
    for surface in surfaces:
        total += int(surface.get("string_count", 0) or 0)
        possible.update(str(item) for item in surface.get("possible_english", []) if item)
    return {
        "schema_version": LOCALIZATION_SURFACE_SCHEMA_VERSION,
        "kind": "localization_surface_summary",
        "string_count": total,
        "possible_english_count": len(possible),
        "possible_english": sorted(possible),
    }


__all__ = ["LOCALIZATION_SURFACE_SCHEMA_VERSION", "build_localization_surface", "merge_localization_surfaces"]
