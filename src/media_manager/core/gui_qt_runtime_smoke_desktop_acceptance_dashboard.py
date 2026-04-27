from __future__ import annotations

from collections.abc import Mapping
from typing import Any

QT_RUNTIME_SMOKE_DESKTOP_ACCEPTANCE_DASHBOARD_SCHEMA_VERSION = "1.0"


def _summary(payload: Mapping[str, Any]) -> Mapping[str, Any]:
    return payload.get("summary") if isinstance(payload.get("summary"), Mapping) else {}


def build_qt_runtime_smoke_desktop_acceptance_dashboard(
    gate: Mapping[str, Any],
    quality: Mapping[str, Any],
    trend: Mapping[str, Any],
    triage: Mapping[str, Any],
) -> dict[str, object]:
    trend_direction = _summary(trend).get("direction")
    issue_count = int(_summary(triage).get("issue_count") or 0)
    cards = [
        {"id": "gate", "title": "Acceptance gate", "value": gate.get("decision"), "severity": "success" if gate.get("ready") else "error"},
        {"id": "quality", "title": "Quality", "value": quality.get("level"), "severity": "success" if quality.get("level") in {"excellent", "good"} else "warning"},
        {"id": "trend", "title": "Trend", "value": trend_direction, "severity": "info"},
        {"id": "issues", "title": "Issues", "value": issue_count, "severity": "error" if issue_count else "success"},
    ]
    return {
        "schema_version": QT_RUNTIME_SMOKE_DESKTOP_ACCEPTANCE_DASHBOARD_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_desktop_acceptance_dashboard",
        "cards": cards,
        "summary": {
            "card_count": len(cards),
            "ready": bool(gate.get("ready")),
            "issue_count": issue_count,
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


__all__ = ["QT_RUNTIME_SMOKE_DESKTOP_ACCEPTANCE_DASHBOARD_SCHEMA_VERSION", "build_qt_runtime_smoke_desktop_acceptance_dashboard"]
