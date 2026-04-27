from __future__ import annotations
from collections.abc import Mapping
from typing import Any

QT_RUNTIME_SMOKE_DESKTOP_START_SUMMARY_SCHEMA_VERSION = "1.0"

def _m(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}

def summarize_qt_runtime_smoke_desktop_start_bundle(bundle: Mapping[str, Any]) -> str:
    summary = _m(bundle.get("summary"))
    command = _m(_m(bundle.get("start_plan")).get("command_line"))
    return "\n".join([
        "Qt runtime smoke desktop start handoff",
        f"  Ready: {bundle.get('ready_for_manual_desktop_start')}",
        f"  Command: {command.get('display_command')}",
        f"  Operator checks: {summary.get('operator_check_count', 0)}",
        f"  Issues: {summary.get('issue_count', 0)}",
        f"  Opens window now: {summary.get('opens_window')}",
        f"  Executes commands now: {summary.get('executes_commands')}",
    ])

__all__ = ["QT_RUNTIME_SMOKE_DESKTOP_START_SUMMARY_SCHEMA_VERSION", "summarize_qt_runtime_smoke_desktop_start_bundle"]
