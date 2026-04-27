from __future__ import annotations

from collections.abc import Mapping
from typing import Any

QT_RUNTIME_SMOKE_DESKTOP_RESULT_SCHEMA_VERSION = "1.0"


def _text(value: object, fallback: str = "") -> str:
    text = str(value).strip() if value is not None else ""
    return text or fallback


def normalize_qt_runtime_smoke_desktop_result(result: Mapping[str, Any], *, index: int = 0) -> dict[str, object]:
    """Normalize a single manual desktop smoke result entry."""

    check_id = _text(result.get("check_id"), f"check-{index + 1}")
    passed = result.get("passed")
    normalized_passed = passed if isinstance(passed, bool) else None
    return {
        "schema_version": QT_RUNTIME_SMOKE_DESKTOP_RESULT_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_desktop_result",
        "check_id": check_id,
        "label": _text(result.get("label"), check_id),
        "required": bool(result.get("required", True)),
        "passed": normalized_passed,
        "note": _text(result.get("note")),
        "has_evidence_path": bool(result.get("evidence_path")),
        "evidence_path": _text(result.get("evidence_path")),
        "local_only": True,
        "contains_sensitive_media": bool(result.get("contains_sensitive_media", False)),
    }


def build_qt_runtime_smoke_desktop_result_schema() -> dict[str, object]:
    return {
        "schema_version": QT_RUNTIME_SMOKE_DESKTOP_RESULT_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_desktop_result_schema",
        "fields": [
            "check_id",
            "label",
            "required",
            "passed",
            "note",
            "has_evidence_path",
            "local_only",
            "contains_sensitive_media",
        ],
        "summary": {
            "field_count": 8,
            "opens_window": False,
            "executes_commands": False,
            "local_only": True,
        },
        "capabilities": {
            "requires_pyside6": False,
            "opens_window": False,
            "headless_testable": True,
            "executes_commands": False,
            "local_only": True,
        },
    }


__all__ = [
    "QT_RUNTIME_SMOKE_DESKTOP_RESULT_SCHEMA_VERSION",
    "build_qt_runtime_smoke_desktop_result_schema",
    "normalize_qt_runtime_smoke_desktop_result",
]
