from __future__ import annotations

from collections.abc import Mapping
from typing import Any

QT_RUNTIME_SMOKE_DESKTOP_ACCEPTANCE_ISSUE_TRIAGE_SCHEMA_VERSION = "1.0"


def _list(value: object) -> list[Any]:
    return value if isinstance(value, list) else []


def build_qt_runtime_smoke_desktop_acceptance_issue_triage(result_bundle: Mapping[str, Any]) -> dict[str, object]:
    audit = result_bundle.get("audit") if isinstance(result_bundle.get("audit"), Mapping) else {}
    issues = []
    for index, problem in enumerate(_list(audit.get("problems"))):
        if not isinstance(problem, Mapping):
            continue
        code = str(problem.get("code") or f"problem-{index + 1}")
        severity = "critical" if "sensitive" in code else "error" if "failed" in code else "warning"
        issues.append({"id": f"triage-{code}", "code": code, "severity": severity, "check_id": problem.get("check_id"), "local_only": True})
    return {
        "schema_version": QT_RUNTIME_SMOKE_DESKTOP_ACCEPTANCE_ISSUE_TRIAGE_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_desktop_acceptance_issue_triage",
        "issues": issues,
        "summary": {
            "issue_count": len(issues),
            "critical_count": sum(1 for issue in issues if issue["severity"] == "critical"),
            "error_count": sum(1 for issue in issues if issue["severity"] == "error"),
            "warning_count": sum(1 for issue in issues if issue["severity"] == "warning"),
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


__all__ = ["QT_RUNTIME_SMOKE_DESKTOP_ACCEPTANCE_ISSUE_TRIAGE_SCHEMA_VERSION", "build_qt_runtime_smoke_desktop_acceptance_issue_triage"]
