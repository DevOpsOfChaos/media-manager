from __future__ import annotations

from collections.abc import Mapping
from typing import Any

QT_RUNTIME_SMOKE_AUDIT_SCHEMA_VERSION = "1.0"


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: object) -> list[Any]:
    return value if isinstance(value, list) else []


def _text(value: object, fallback: str = "") -> str:
    text = str(value).strip() if value is not None else ""
    return text or fallback


def audit_qt_runtime_smoke_session(smoke_session: Mapping[str, Any]) -> dict[str, object]:
    """Audit a manual smoke session for required checks and privacy coverage."""

    problems: list[dict[str, object]] = []
    missing = [str(item) for item in _list(smoke_session.get("missing_required_checks"))]
    failed = [str(item) for item in _list(smoke_session.get("failed_required_checks"))]
    checks = [check for check in _list(smoke_session.get("checks")) if isinstance(check, Mapping)]

    for check_id in missing:
        problems.append({"code": "missing_required_smoke_check", "check_id": check_id})
    for check_id in failed:
        problems.append({"code": "failed_required_smoke_check", "check_id": check_id})

    privacy_checks = [check for check in checks if check.get("category") == "privacy"]
    privacy_required = [check for check in privacy_checks if check.get("required", True)]
    passed_privacy = [check for check in privacy_required if check.get("passed") is True]
    failed_privacy = [check for check in privacy_required if check.get("passed") is False]

    if privacy_required and len(passed_privacy) != len(privacy_required):
        problems.append(
            {
                "code": "privacy_smoke_incomplete",
                "required_privacy_check_count": len(privacy_required),
                "passed_privacy_check_count": len(passed_privacy),
            }
        )

    for check in failed_privacy:
        problems.append({"code": "privacy_smoke_failed", "check_id": _text(check.get("check_id"))})

    summary = _mapping(smoke_session.get("summary"))
    valid = not problems and bool(smoke_session.get("complete"))
    return {
        "schema_version": QT_RUNTIME_SMOKE_AUDIT_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_audit",
        "valid": valid,
        "problem_count": len(problems),
        "problems": problems,
        "summary": {
            "check_count": summary.get("check_count", 0),
            "result_count": summary.get("result_count", 0),
            "missing_required_count": len(missing),
            "failed_required_count": len(failed),
            "privacy_check_count": len(privacy_checks),
            "passed_privacy_check_count": len(passed_privacy),
        },
        "capabilities": {
            "requires_pyside6": False,
            "opens_window": False,
            "headless_testable": True,
            "executes_commands": False,
            "local_only": True,
        },
    }


__all__ = ["QT_RUNTIME_SMOKE_AUDIT_SCHEMA_VERSION", "audit_qt_runtime_smoke_session"]
