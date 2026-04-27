from __future__ import annotations

from collections.abc import Mapping
from typing import Any

QT_RUNTIME_SMOKE_DESKTOP_REHEARSAL_SUMMARY_SCHEMA_VERSION = "1.0"


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def summarize_qt_runtime_smoke_desktop_rehearsal_bundle(bundle: Mapping[str, Any]) -> str:
    summary = _mapping(bundle.get("summary"))
    launch_notes = _mapping(bundle.get("launch_notes"))
    return "\n".join(
        [
            "Qt runtime smoke desktop rehearsal bundle",
            f"  Ready: {bundle.get('ready_for_manual_desktop_smoke')}",
            f"  Manual steps: {summary.get('manual_step_count', 0)}",
            f"  Hints: {summary.get('hint_count', 0)}",
            f"  Audit problems: {summary.get('audit_problem_count', 0)}",
            f"  Command: {launch_notes.get('display_command')}",
            f"  Opens window: {summary.get('opens_window')}",
            f"  Executes commands: {summary.get('executes_commands')}",
        ]
    )


__all__ = ["QT_RUNTIME_SMOKE_DESKTOP_REHEARSAL_SUMMARY_SCHEMA_VERSION", "summarize_qt_runtime_smoke_desktop_rehearsal_bundle"]
