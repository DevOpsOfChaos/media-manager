from __future__ import annotations

from collections.abc import Mapping
from typing import Any

QT_RUNTIME_SMOKE_DESKTOP_ACCEPTANCE_SUMMARY_SCHEMA_VERSION = "1.0"


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def summarize_qt_runtime_smoke_desktop_acceptance_bundle(bundle: Mapping[str, Any]) -> str:
    summary = _mapping(bundle.get("summary"))
    return "\n".join(
        [
            "Qt runtime smoke desktop acceptance",
            f"  Accepted: {bundle.get('accepted')}",
            f"  Quality: {summary.get('quality_level')}",
            f"  Problems: {summary.get('problem_count', 0)}",
            f"  Issues: {summary.get('issue_count', 0)}",
            f"  Regressed: {summary.get('regressed')}",
            f"  Opens window: {summary.get('opens_window')}",
            f"  Executes commands: {summary.get('executes_commands')}",
        ]
    )


__all__ = ["QT_RUNTIME_SMOKE_DESKTOP_ACCEPTANCE_SUMMARY_SCHEMA_VERSION", "summarize_qt_runtime_smoke_desktop_acceptance_bundle"]
