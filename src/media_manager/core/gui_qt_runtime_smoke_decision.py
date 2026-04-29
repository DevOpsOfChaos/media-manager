from __future__ import annotations

from collections.abc import Mapping
from typing import Any

QT_RUNTIME_SMOKE_DECISION_SCHEMA_VERSION = "1.0"


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _int(value: object, fallback: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return fallback


def build_qt_runtime_smoke_decision(dashboard: Mapping[str, Any]) -> dict[str, object]:
    summary = _mapping(dashboard.get("summary"))
    blocked = _int(summary.get("blocked_badge_count"))
    current_ready = bool(summary.get("current_ready"))
    if blocked:
        decision, action, severity = "blocked", "Fix failing runtime smoke checks before manual launch.", "error"
    elif current_ready:
        if bool(summary.get("evidence_complete")):
            action = "Manual Qt smoke evidence is complete; release-gate review may continue."
        else:
            action = "Manual Qt smoke attempt may be started by the user; evidence is still pending until results are recorded."
        decision, severity = "ready_for_manual_qt_smoke", "success"
    else:
        decision, action, severity = "pending", "Record a runtime smoke report before launch.", "info"
    return {
        "schema_version": QT_RUNTIME_SMOKE_DECISION_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_decision",
        "active_page_id": dashboard.get("active_page_id"),
        "decision": decision,
        "severity": severity,
        "recommended_next_step": action,
        "requires_user_confirmation": True,
        "executes_immediately": False,
        "opens_window": False,
        "capabilities": {"requires_pyside6": False, "opens_window": False, "headless_testable": True, "executes_commands": False, "local_only": True},
    }


def summarize_qt_runtime_smoke_decision(decision: Mapping[str, Any]) -> str:
    return "\n".join([
        "Qt runtime smoke decision",
        f"  Active page: {decision.get('active_page_id')}",
        f"  Decision: {decision.get('decision')}",
        f"  Severity: {decision.get('severity')}",
        f"  Opens window: {decision.get('opens_window')}",
        f"  Executes immediately: {decision.get('executes_immediately')}",
    ])


__all__ = ["QT_RUNTIME_SMOKE_DECISION_SCHEMA_VERSION", "build_qt_runtime_smoke_decision", "summarize_qt_runtime_smoke_decision"]
