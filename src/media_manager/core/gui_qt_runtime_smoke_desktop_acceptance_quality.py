from __future__ import annotations

from collections.abc import Mapping
from typing import Any

QT_RUNTIME_SMOKE_DESKTOP_ACCEPTANCE_QUALITY_SCHEMA_VERSION = "1.0"


def build_qt_runtime_smoke_desktop_acceptance_quality(acceptance_input: Mapping[str, Any], gate: Mapping[str, Any]) -> dict[str, object]:
    summary = acceptance_input.get("summary") if isinstance(acceptance_input.get("summary"), Mapping) else {}
    result_count = int(summary.get("result_count") or 0)
    issue_count = int(summary.get("issue_count") or 0)
    score = 100
    score -= min(50, issue_count * 20)
    if not gate.get("ready"):
        score -= 25
    if result_count < 5:
        score -= 10
    score = max(0, score)
    level = "excellent" if score >= 90 else "good" if score >= 75 else "needs_attention" if score >= 50 else "blocked"
    return {
        "schema_version": QT_RUNTIME_SMOKE_DESKTOP_ACCEPTANCE_QUALITY_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_desktop_acceptance_quality",
        "score": score,
        "level": level,
        "signals": {
            "result_count": result_count,
            "issue_count": issue_count,
            "gate_ready": bool(gate.get("ready")),
        },
        "summary": {
            "score": score,
            "level": level,
            "ready": level in {"excellent", "good"} and bool(gate.get("ready")),
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


__all__ = ["QT_RUNTIME_SMOKE_DESKTOP_ACCEPTANCE_QUALITY_SCHEMA_VERSION", "build_qt_runtime_smoke_desktop_acceptance_quality"]
