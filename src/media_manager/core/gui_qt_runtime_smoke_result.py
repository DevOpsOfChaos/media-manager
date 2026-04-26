from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timezone
from typing import Any

QT_RUNTIME_SMOKE_RESULT_SCHEMA_VERSION = "1.0"


def _now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: object) -> list[Any]:
    return value if isinstance(value, list) else []


def _text(value: object, fallback: str = "") -> str:
    text = str(value).strip() if value is not None else ""
    return text or fallback


def build_qt_runtime_smoke_result(
    check_id: str,
    *,
    passed: bool,
    note: str = "",
    category: str = "",
    required: bool = True,
    evidence_path: str | None = None,
    reviewer: str = "",
    recorded_at_utc: str | None = None,
) -> dict[str, object]:
    """Record one manual smoke-check result as plain, local data."""

    check = _text(check_id, "check")
    return {
        "schema_version": QT_RUNTIME_SMOKE_RESULT_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_result",
        "check_id": check,
        "passed": bool(passed),
        "required": bool(required),
        "category": _text(category, "manual"),
        "note": _text(note),
        "evidence_path": evidence_path,
        "reviewer": _text(reviewer),
        "recorded_at_utc": recorded_at_utc or _now_utc(),
        "capabilities": {
            "requires_pyside6": False,
            "opens_window": False,
            "headless_testable": True,
            "executes_commands": False,
            "local_only": True,
        },
    }


def build_qt_runtime_smoke_result_from_check(
    check: Mapping[str, Any],
    *,
    passed: bool,
    note: str = "",
    evidence_path: str | None = None,
    reviewer: str = "",
) -> dict[str, object]:
    """Record a result while preserving metadata from a smoke-plan check."""

    return build_qt_runtime_smoke_result(
        _text(check.get("id"), "check"),
        passed=passed,
        note=note,
        category=_text(check.get("category"), "manual"),
        required=bool(check.get("required", True)),
        evidence_path=evidence_path,
        reviewer=reviewer,
    )


def normalize_qt_runtime_smoke_results(results: Mapping[str, bool] | list[Mapping[str, Any]]) -> list[dict[str, object]]:
    """Normalize either a check-id -> bool mapping or result objects."""

    if isinstance(results, Mapping):
        return [
            build_qt_runtime_smoke_result(str(check_id), passed=bool(passed), recorded_at_utc="manual")
            for check_id, passed in sorted(results.items())
        ]
    normalized: list[dict[str, object]] = []
    for item in _list(results):
        if not isinstance(item, Mapping):
            continue
        if item.get("kind") == "qt_runtime_smoke_result":
            normalized.append(dict(item))
        else:
            normalized.append(
                build_qt_runtime_smoke_result(
                    _text(item.get("check_id") or item.get("id"), "check"),
                    passed=bool(item.get("passed")),
                    note=_text(item.get("note")),
                    category=_text(item.get("category"), "manual"),
                    required=bool(item.get("required", True)),
                    evidence_path=item.get("evidence_path") if isinstance(item.get("evidence_path"), str) else None,
                    reviewer=_text(item.get("reviewer")),
                    recorded_at_utc=_text(item.get("recorded_at_utc")) or None,
                )
            )
    return normalized


def summarize_qt_runtime_smoke_results(results: Mapping[str, bool] | list[Mapping[str, Any]]) -> dict[str, object]:
    normalized = normalize_qt_runtime_smoke_results(results)
    return {
        "schema_version": QT_RUNTIME_SMOKE_RESULT_SCHEMA_VERSION,
        "result_count": len(normalized),
        "passed_count": sum(1 for result in normalized if result.get("passed") is True),
        "failed_count": sum(1 for result in normalized if result.get("passed") is False),
        "required_result_count": sum(1 for result in normalized if result.get("required")),
        "failed_required_count": sum(1 for result in normalized if result.get("required") and result.get("passed") is False),
        "privacy_result_count": sum(1 for result in normalized if result.get("category") == "privacy"),
    }


__all__ = [
    "QT_RUNTIME_SMOKE_RESULT_SCHEMA_VERSION",
    "build_qt_runtime_smoke_result",
    "build_qt_runtime_smoke_result_from_check",
    "normalize_qt_runtime_smoke_results",
    "summarize_qt_runtime_smoke_results",
]
