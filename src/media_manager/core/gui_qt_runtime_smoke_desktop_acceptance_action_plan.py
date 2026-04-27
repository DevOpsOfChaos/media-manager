from __future__ import annotations

from collections.abc import Mapping
from typing import Any

QT_RUNTIME_SMOKE_DESKTOP_ACCEPTANCE_ACTION_PLAN_SCHEMA_VERSION = "1.0"


def build_qt_runtime_smoke_desktop_acceptance_action_plan(gate: Mapping[str, Any], triage: Mapping[str, Any]) -> dict[str, object]:
    ready = bool(gate.get("ready")) and int(triage.get("summary", {}).get("issue_count", 0)) == 0 if isinstance(triage.get("summary"), Mapping) else bool(gate.get("ready"))
    actions = [
        {"id": "record-acceptance", "label": "Record desktop smoke acceptance", "enabled": ready, "requires_confirmation": True},
        {"id": "export-metadata", "label": "Export redacted metadata", "enabled": True, "requires_confirmation": False},
        {"id": "open-follow-up", "label": "Open follow-up task for failed checks", "enabled": not ready, "requires_confirmation": True},
    ]
    return {
        "schema_version": QT_RUNTIME_SMOKE_DESKTOP_ACCEPTANCE_ACTION_PLAN_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_desktop_acceptance_action_plan",
        "actions": [{**action, "executes_immediately": False} for action in actions],
        "summary": {
            "action_count": len(actions),
            "enabled_action_count": sum(1 for action in actions if action["enabled"]),
            "confirmation_action_count": sum(1 for action in actions if action["requires_confirmation"]),
            "immediate_execution_count": 0,
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


__all__ = ["QT_RUNTIME_SMOKE_DESKTOP_ACCEPTANCE_ACTION_PLAN_SCHEMA_VERSION", "build_qt_runtime_smoke_desktop_acceptance_action_plan"]
