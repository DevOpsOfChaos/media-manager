from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .gui_qt_runtime_smoke_desktop_result_schema import normalize_qt_runtime_smoke_desktop_result

QT_RUNTIME_SMOKE_DESKTOP_RESULT_VALIDATOR_SCHEMA_VERSION = "1.0"


def _list(value: object) -> list[Any]:
    return value if isinstance(value, list) else []


def collect_qt_runtime_smoke_desktop_results(payload: Mapping[str, Any] | list[Mapping[str, Any]]) -> list[dict[str, object]]:
    source = payload.get("results") if isinstance(payload, Mapping) else payload
    return [
        normalize_qt_runtime_smoke_desktop_result(result, index=index)
        for index, result in enumerate(_list(source))
        if isinstance(result, Mapping)
    ]


def validate_qt_runtime_smoke_desktop_results(payload: Mapping[str, Any] | list[Mapping[str, Any]]) -> dict[str, object]:
    """Validate manual desktop smoke results without reading evidence files."""

    results = collect_qt_runtime_smoke_desktop_results(payload)
    problems: list[dict[str, object]] = []
    seen: set[str] = set()
    for result in results:
        check_id = str(result["check_id"])
        if check_id in seen:
            problems.append({"code": "duplicate_check_id", "check_id": check_id})
        seen.add(check_id)
        if result["required"] and result["passed"] is None:
            problems.append({"code": "missing_required_result", "check_id": check_id})
        if result["required"] and result["passed"] is False:
            problems.append({"code": "failed_required_result", "check_id": check_id})
        if result["contains_sensitive_media"]:
            problems.append({"code": "sensitive_media_attached", "check_id": check_id})
    return {
        "schema_version": QT_RUNTIME_SMOKE_DESKTOP_RESULT_VALIDATOR_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_desktop_result_validation",
        "valid": not problems,
        "problem_count": len(problems),
        "problems": problems,
        "results": results,
        "summary": {
            "result_count": len(results),
            "required_result_count": sum(1 for result in results if result["required"]),
            "passed_required_count": sum(1 for result in results if result["required"] and result["passed"] is True),
            "failed_required_count": sum(1 for result in results if result["required"] and result["passed"] is False),
            "missing_required_count": sum(1 for result in results if result["required"] and result["passed"] is None),
            "sensitive_media_count": sum(1 for result in results if result["contains_sensitive_media"]),
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
    "QT_RUNTIME_SMOKE_DESKTOP_RESULT_VALIDATOR_SCHEMA_VERSION",
    "collect_qt_runtime_smoke_desktop_results",
    "validate_qt_runtime_smoke_desktop_results",
]
