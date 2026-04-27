from __future__ import annotations
from collections.abc import Mapping
from typing import Any

QT_RUNTIME_SMOKE_DESKTOP_START_AUDIT_SCHEMA_VERSION = "1.0"

def _m(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}

def audit_qt_runtime_smoke_desktop_start(start_plan: Mapping[str, Any], manifest: Mapping[str, Any], issue_report: Mapping[str, Any]) -> dict[str, object]:
    problems: list[dict[str, object]] = []
    start_summary = _m(start_plan.get("summary"))
    manifest_summary = _m(manifest.get("summary"))
    issue_summary = _m(issue_report.get("summary"))
    if start_plan.get("ready_for_manual_start") is not True:
        problems.append({"code": "start_plan_not_ready"})
    if manifest_summary.get("local_only") is not True:
        problems.append({"code": "manifest_not_local_only"})
    if issue_summary.get("has_blocking_issues"):
        problems.append({"code": "desktop_smoke_has_blocking_issues"})
    if start_summary.get("opens_window") is not False or manifest_summary.get("opens_window") is not False:
        problems.append({"code": "headless_plan_opens_window"})
    if start_summary.get("executes_commands") is not False or manifest_summary.get("executes_commands") is not False:
        problems.append({"code": "headless_plan_executes_commands"})
    return {
        "schema_version": QT_RUNTIME_SMOKE_DESKTOP_START_AUDIT_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_desktop_start_audit",
        "valid": not problems,
        "problem_count": len(problems),
        "problems": problems,
        "summary": {"valid": not problems, "issue_count": issue_summary.get("issue_count", 0), "opens_window": False, "executes_commands": False, "local_only": True},
        "capabilities": {"requires_pyside6": False, "opens_window": False, "headless_testable": True, "executes_commands": False, "local_only": True},
    }

__all__ = ["QT_RUNTIME_SMOKE_DESKTOP_START_AUDIT_SCHEMA_VERSION", "audit_qt_runtime_smoke_desktop_start"]
