from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

BATCH_ACTION_PANEL_SCHEMA_VERSION = "1.0"

_DEFAULT_ACTIONS = ("accept_selected", "reject_selected", "mark_needs_review", "clear_selection")
_RISKY_ACTIONS = {"apply_selected", "delete_selected", "export_encodings"}


def build_batch_action_panel(
    *,
    selected_count: int = 0,
    action_ids: Iterable[str] | None = None,
    allow_apply: bool = False,
) -> dict[str, object]:
    normalized_count = max(0, int(selected_count))
    actions = []
    for action_id in action_ids or _DEFAULT_ACTIONS:
        action = str(action_id)
        risky = action in _RISKY_ACTIONS or action.startswith("apply")
        enabled = normalized_count > 0 and (allow_apply or not risky)
        actions.append(
            {
                "id": action,
                "label": action.replace("_", " ").title(),
                "enabled": enabled,
                "risk_level": "high" if risky else "safe",
                "requires_confirmation": risky,
                "executes_immediately": False,
                "blocked_reason": None if enabled else "Select at least one item." if normalized_count == 0 else "Confirmation or preview is required.",
            }
        )
    return {
        "schema_version": BATCH_ACTION_PANEL_SCHEMA_VERSION,
        "kind": "qt_batch_action_panel",
        "selected_count": normalized_count,
        "action_count": len(actions),
        "enabled_action_count": sum(1 for action in actions if action["enabled"]),
        "confirmation_action_count": sum(1 for action in actions if action["requires_confirmation"]),
        "actions": actions,
    }


def batch_action_summary(panel: Mapping[str, Any]) -> dict[str, object]:
    return {
        "selected_count": panel.get("selected_count", 0),
        "enabled_action_count": panel.get("enabled_action_count", 0),
        "confirmation_action_count": panel.get("confirmation_action_count", 0),
    }


__all__ = ["BATCH_ACTION_PANEL_SCHEMA_VERSION", "batch_action_summary", "build_batch_action_panel"]
