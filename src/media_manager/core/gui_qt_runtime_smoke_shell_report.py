from __future__ import annotations
from collections.abc import Mapping
from typing import Any
QT_RUNTIME_SMOKE_SHELL_REPORT_SCHEMA_VERSION = "1.0"
def _mapping(value: object) -> Mapping[str, Any]: return value if isinstance(value, Mapping) else {}
def build_qt_runtime_smoke_shell_report(shell_bundle: Mapping[str, Any]) -> dict[str, object]:
    readiness = _mapping(shell_bundle.get("readiness")); registration = _mapping(shell_bundle.get("shell_registration")); summary = _mapping(readiness.get("summary"))
    return {"schema_version": QT_RUNTIME_SMOKE_SHELL_REPORT_SCHEMA_VERSION, "kind": "qt_runtime_smoke_shell_report", "page_id": registration.get("page_id"), "ready": bool(readiness.get("ready")), "summary": {"problem_count": int(readiness.get("problem_count") or 0), "command_count": summary.get("command_count", 0), "toolbar_button_count": summary.get("toolbar_button_count", 0), "local_only": summary.get("local_only", True), "opens_window": False, "executes_commands": False}, "message": "Runtime Smoke shell integration is ready." if readiness.get("ready") else "Runtime Smoke shell integration needs attention.", "capabilities": {"requires_pyside6": False, "opens_window": False, "headless_testable": True, "executes_commands": False, "local_only": True}}
def summarize_qt_runtime_smoke_shell_report(report: Mapping[str, Any]) -> str:
    summary = _mapping(report.get("summary")); return "\n".join(["Qt runtime smoke shell report", f"  Page: {report.get('page_id')}", f"  Ready: {report.get('ready')}", f"  Problems: {summary.get('problem_count', 0)}", f"  Commands: {summary.get('command_count', 0)}", f"  Toolbar buttons: {summary.get('toolbar_button_count', 0)}", f"  Opens window: {summary.get('opens_window')}", f"  Executes commands: {summary.get('executes_commands')}"])
__all__ = ["QT_RUNTIME_SMOKE_SHELL_REPORT_SCHEMA_VERSION", "build_qt_runtime_smoke_shell_report", "summarize_qt_runtime_smoke_shell_report"]
