from __future__ import annotations

from collections.abc import Mapping
from typing import Any

QT_RUNTIME_SMOKE_NAVIGATION_SUMMARY_SCHEMA_VERSION = "1.0"


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def summarize_qt_runtime_smoke_page_handoff(page_handoff: Mapping[str, Any]) -> str:
    summary = _mapping(page_handoff.get("summary"))
    route = _mapping(page_handoff.get("route"))
    diagnostics = _mapping(page_handoff.get("diagnostics"))
    return "\n".join(
        [
            "Qt runtime smoke page handoff",
            f"  Route: {route.get('route_id')}",
            f"  Page: {route.get('page_id')}",
            f"  Ready for shell registration: {page_handoff.get('ready_for_shell_registration')}",
            f"  Pages: {summary.get('page_count', 0)}",
            f"  Problems: {summary.get('problem_count', 0)}",
            f"  Diagnostics ready: {diagnostics.get('ready')}",
            f"  Opens window: {summary.get('opens_window')}",
            f"  Executes commands: {summary.get('executes_commands')}",
        ]
    )


__all__ = ["QT_RUNTIME_SMOKE_NAVIGATION_SUMMARY_SCHEMA_VERSION", "summarize_qt_runtime_smoke_page_handoff"]
