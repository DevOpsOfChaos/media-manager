from __future__ import annotations

from collections.abc import Mapping
from typing import Any

QT_RUNTIME_SMOKE_DESKTOP_RESULT_SUMMARY_TEXT_SCHEMA_VERSION = "1.0"


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def summarize_qt_runtime_smoke_desktop_result_bundle(bundle: Mapping[str, Any]) -> str:
    summary = _mapping(bundle.get("summary"))
    return "\n".join(
        [
            "Qt runtime smoke desktop results",
            f"  Accepted: {bundle.get('accepted')}",
            f"  Decision: {summary.get('decision')}",
            f"  Results: {summary.get('result_count', 0)}",
            f"  Failed required: {summary.get('failed_required_count', 0)}",
            f"  Missing required: {summary.get('missing_required_count', 0)}",
            f"  Opens window: {summary.get('opens_window')}",
            f"  Executes commands: {summary.get('executes_commands')}",
        ]
    )


__all__ = ["QT_RUNTIME_SMOKE_DESKTOP_RESULT_SUMMARY_TEXT_SCHEMA_VERSION", "summarize_qt_runtime_smoke_desktop_result_bundle"]
