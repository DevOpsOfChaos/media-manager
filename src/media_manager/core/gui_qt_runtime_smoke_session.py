from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .gui_qt_runtime_smoke_result import normalize_qt_runtime_smoke_results, summarize_qt_runtime_smoke_results

QT_RUNTIME_SMOKE_SESSION_SCHEMA_VERSION = "1.0"


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: object) -> list[Any]:
    return value if isinstance(value, list) else []


def _text(value: object, fallback: str = "") -> str:
    text = str(value).strip() if value is not None else ""
    return text or fallback


def _check_id(check: Mapping[str, Any]) -> str:
    return _text(check.get("id"), "check")


def build_qt_runtime_smoke_session(
    smoke_plan: Mapping[str, Any],
    results: Mapping[str, bool] | list[Mapping[str, Any]],
    *,
    reviewer: str = "",
) -> dict[str, object]:
    """Merge a manual smoke plan with recorded results."""

    checks = [check for check in _list(smoke_plan.get("checks")) if isinstance(check, Mapping)]
    normalized_results = normalize_qt_runtime_smoke_results(results)
    result_by_check = {str(result.get("check_id")): result for result in normalized_results}
    check_rows: list[dict[str, object]] = []
    missing_required: list[str] = []
    failed_required: list[str] = []

    for check in checks:
        check_id = _check_id(check)
        result = _mapping(result_by_check.get(check_id))
        passed = result.get("passed") if result else None
        required = bool(check.get("required", True))
        row = {
            "check_id": check_id,
            "label": check.get("label"),
            "category": _text(check.get("category"), "manual"),
            "required": required,
            "passed": passed,
            "has_result": bool(result),
            "note": result.get("note") if result else "",
            "evidence_path": result.get("evidence_path") if result else None,
        }
        check_rows.append(row)
        if required and not result:
            missing_required.append(check_id)
        elif required and passed is False:
            failed_required.append(check_id)

    extra_results = sorted(check_id for check_id in result_by_check if check_id not in {_check_id(check) for check in checks})
    result_summary = summarize_qt_runtime_smoke_results(normalized_results)
    summary = {
        "schema_version": QT_RUNTIME_SMOKE_SESSION_SCHEMA_VERSION,
        "check_count": len(checks),
        "required_check_count": sum(1 for check in checks if check.get("required", True)),
        "result_count": result_summary.get("result_count", 0),
        "passed_count": result_summary.get("passed_count", 0),
        "failed_count": result_summary.get("failed_count", 0),
        "missing_required_count": len(missing_required),
        "failed_required_count": len(failed_required),
        "extra_result_count": len(extra_results),
        "privacy_check_count": sum(1 for check in checks if check.get("category") == "privacy"),
    }
    complete = summary["missing_required_count"] == 0 and summary["failed_required_count"] == 0
    return {
        "schema_version": QT_RUNTIME_SMOKE_SESSION_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_session",
        "active_page_id": smoke_plan.get("active_page_id"),
        "language": smoke_plan.get("language"),
        "reviewer": _text(reviewer),
        "checks": check_rows,
        "results": normalized_results,
        "missing_required_checks": missing_required,
        "failed_required_checks": failed_required,
        "extra_results": extra_results,
        "summary": summary,
        "complete": complete,
        "capabilities": {
            "requires_pyside6": False,
            "opens_window": False,
            "headless_testable": True,
            "executes_commands": False,
            "local_only": True,
        },
    }


__all__ = ["QT_RUNTIME_SMOKE_SESSION_SCHEMA_VERSION", "build_qt_runtime_smoke_session"]
