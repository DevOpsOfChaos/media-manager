from __future__ import annotations

from collections.abc import Mapping
from typing import Any

QT_RUNTIME_SMOKE_WORKBENCH_ACTIONS_SCHEMA_VERSION = "1.0"


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _text(value: object, fallback: str = "") -> str:
    text = str(value).strip() if value is not None else ""
    return text or fallback


def _action(action_id: str, label: str, *, enabled: bool, requires_confirmation: bool = False, danger: bool = False) -> dict[str, object]:
    return {
        "id": action_id,
        "label": label,
        "enabled": bool(enabled),
        "requires_confirmation": bool(requires_confirmation),
        "danger": bool(danger),
        "executes_immediately": False,
    }


def build_qt_runtime_smoke_workbench_actions(workbench: Mapping[str, Any]) -> dict[str, object]:
    """Build non-executing UI action descriptors for the smoke workbench."""

    summary = _mapping(workbench.get("summary"))
    ready = bool(summary.get("ready_for_runtime_review"))
    status = _text(workbench.get("status"), "pending")
    actions = [
        _action("refresh-runtime-smoke", "Refresh smoke data", enabled=True),
        _action("open-manual-smoke-checklist", "Open manual smoke checklist", enabled=True),
        _action("export-smoke-metadata", "Export smoke metadata", enabled=ready),
        _action("start-manual-qt-smoke", "Start manual Qt smoke", enabled=ready, requires_confirmation=True),
    ]
    if status == "blocked":
        actions.append(_action("review-failed-smoke-checks", "Review failed smoke checks", enabled=True, danger=True))
    elif status == "incomplete":
        actions.append(_action("complete-missing-smoke-results", "Complete missing results", enabled=True))
    return {
        "schema_version": QT_RUNTIME_SMOKE_WORKBENCH_ACTIONS_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_workbench_actions",
        "active_page_id": workbench.get("active_page_id"),
        "actions": actions,
        "summary": {
            "action_count": len(actions),
            "enabled_action_count": sum(1 for action in actions if action["enabled"]),
            "confirmation_action_count": sum(1 for action in actions if action["requires_confirmation"]),
            "danger_action_count": sum(1 for action in actions if action["danger"]),
        },
        "capabilities": {
            "requires_pyside6": False,
            "opens_window": False,
            "headless_testable": True,
            "executes_commands": False,
            "local_only": True,
        },
    }


__all__ = ["QT_RUNTIME_SMOKE_WORKBENCH_ACTIONS_SCHEMA_VERSION", "build_qt_runtime_smoke_workbench_actions"]
