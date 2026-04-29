from __future__ import annotations

from collections.abc import Mapping
from typing import Any

QT_RUNTIME_SMOKE_GUARDED_SUMMARY_SCHEMA_VERSION = "1.0"


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def summarize_guarded_qt_runtime_smoke_integration(guarded_integration: Mapping[str, Any]) -> str:
    summary = _mapping(guarded_integration.get("summary"))
    manual = _mapping(_mapping(guarded_integration.get("manual_readiness")).get("summary"))
    return "\n".join(
        [
            "Guarded Qt Runtime Smoke integration",
            f"  Page: {guarded_integration.get('page_id')}",
            f"  Ready for shell route: {summary.get('ready_for_shell_route')}",
            f"  Ready to start manual smoke: {manual.get('ready_to_start_manual_smoke')}",
            f"  Problem count: {summary.get('problem_count', 0)}",
            f"  Opens window now: {summary.get('opens_window')}",
            f"  Executes commands now: {summary.get('executes_commands')}",
            f"  Local only: {summary.get('local_only')}",
        ]
    )


__all__ = ["QT_RUNTIME_SMOKE_GUARDED_SUMMARY_SCHEMA_VERSION", "summarize_guarded_qt_runtime_smoke_integration"]
