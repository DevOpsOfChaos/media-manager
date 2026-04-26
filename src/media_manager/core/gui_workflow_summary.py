from __future__ import annotations

from collections.abc import Mapping
from typing import Any

WORKFLOW_SUMMARY_SCHEMA_VERSION = "1.0"


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def summarize_gui_workflow(*, board: Mapping[str, Any] | None = None, checklist: Mapping[str, Any] | None = None, insights: Mapping[str, Any] | None = None) -> dict[str, object]:
    board_summary = _mapping(_mapping(board).get("summary"))
    checklist_payload = _mapping(checklist)
    insights_payload = _mapping(insights)
    blocked_count = int(board_summary.get("blocked_count", 0) or 0) + int(checklist_payload.get("blocking_count", 0) or 0)
    warning_count = int(insights_payload.get("warning_count", 0) or 0)
    return {
        "schema_version": WORKFLOW_SUMMARY_SCHEMA_VERSION,
        "kind": "gui_workflow_summary",
        "ready": blocked_count == 0,
        "blocked_count": blocked_count,
        "warning_count": warning_count,
        "card_count": board_summary.get("card_count", 0),
        "checklist_ready": checklist_payload.get("ready"),
        "next_action_id": insights_payload.get("next_action_id"),
    }


__all__ = ["WORKFLOW_SUMMARY_SCHEMA_VERSION", "summarize_gui_workflow"]
