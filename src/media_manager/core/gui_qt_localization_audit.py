from __future__ import annotations

from collections.abc import Mapping
from typing import Any

LOCALIZATION_AUDIT_SCHEMA_VERSION = "1.0"


def _walk_strings(value: Any, path: str = "root") -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    if isinstance(value, str):
        if value.strip():
            rows.append({"path": path, "text": value})
    elif isinstance(value, Mapping):
        for key, item in value.items():
            rows.extend(_walk_strings(item, f"{path}.{key}"))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            rows.extend(_walk_strings(item, f"{path}[{index}]"))
    return rows


def audit_qt_localization(model: Mapping[str, Any], *, language: str = "de") -> dict[str, object]:
    strings = _walk_strings(model)
    english_markers = []
    if str(language).lower().startswith("de"):
        common_english = ("review", "settings", "dashboard", "profiles", "run history", "ready")
        for row in strings:
            text = row["text"].casefold()
            if any(marker in text for marker in common_english):
                english_markers.append(row)
    return {
        "schema_version": LOCALIZATION_AUDIT_SCHEMA_VERSION,
        "kind": "qt_localization_audit",
        "language": language,
        "string_count": len(strings),
        "possible_english_count": len(english_markers),
        "possible_english": english_markers[:50],
        "ok": len(english_markers) == 0,
    }


__all__ = ["LOCALIZATION_AUDIT_SCHEMA_VERSION", "audit_qt_localization"]
