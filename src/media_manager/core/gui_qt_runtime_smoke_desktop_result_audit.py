from __future__ import annotations

from collections.abc import Mapping
from typing import Any

QT_RUNTIME_SMOKE_DESKTOP_RESULT_AUDIT_SCHEMA_VERSION = "1.0"


def _list(value: object) -> list[Any]:
    return value if isinstance(value, list) else []


def audit_qt_runtime_smoke_desktop_results(validation: Mapping[str, Any]) -> dict[str, object]:
    problems: list[dict[str, object]] = []
    for problem in _list(validation.get("problems")):
        if isinstance(problem, Mapping):
            problems.append(dict(problem))
    for result in _list(validation.get("results")):
        if not isinstance(result, Mapping):
            continue
        if result.get("contains_sensitive_media"):
            problems.append({"code": "sensitive_media_must_not_be_shared", "check_id": result.get("check_id")})
        if result.get("evidence_path") and not result.get("local_only", True):
            problems.append({"code": "non_local_evidence_path", "check_id": result.get("check_id")})
    return {
        "schema_version": QT_RUNTIME_SMOKE_DESKTOP_RESULT_AUDIT_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_desktop_result_audit",
        "valid": not problems,
        "problem_count": len(problems),
        "problems": problems,
        "summary": {
            "valid": not problems,
            "privacy_problem_count": sum(1 for problem in problems if "sensitive" in str(problem.get("code")) or "evidence" in str(problem.get("code"))),
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


__all__ = ["QT_RUNTIME_SMOKE_DESKTOP_RESULT_AUDIT_SCHEMA_VERSION", "audit_qt_runtime_smoke_desktop_results"]
