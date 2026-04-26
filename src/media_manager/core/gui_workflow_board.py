from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

WORKFLOW_BOARD_SCHEMA_VERSION = "1.0"
DEFAULT_COLUMNS = ("todo", "in_progress", "review", "ready", "blocked", "done")

_STATUS_TO_COLUMN = {
    "new": "todo",
    "todo": "todo",
    "pending": "todo",
    "running": "in_progress",
    "in_progress": "in_progress",
    "needs_review": "review",
    "needs_name": "review",
    "ready": "ready",
    "ready_to_apply": "ready",
    "blocked": "blocked",
    "error": "blocked",
    "failed": "blocked",
    "done": "done",
    "completed": "done",
    "ok": "done",
}


def _text(value: object, default: str = "") -> str:
    text = str(value).strip() if value is not None else ""
    return text or default


def _bool(value: object, default: bool = False) -> bool:
    return value if isinstance(value, bool) else default


def normalize_workflow_status(status: object) -> str:
    raw = _text(status, "todo").lower().replace(" ", "_").replace("-", "_")
    return raw if raw in _STATUS_TO_COLUMN else "todo"


def column_for_status(status: object) -> str:
    return _STATUS_TO_COLUMN[normalize_workflow_status(status)]


def build_workflow_card(
    card_id: str,
    title: str,
    *,
    status: str = "todo",
    subtitle: str = "",
    source: str = "manual",
    payload: Mapping[str, Any] | None = None,
    actions: Iterable[Mapping[str, Any]] = (),
) -> dict[str, object]:
    normalized_status = normalize_workflow_status(status)
    action_list = [dict(action) for action in actions]
    return {
        "schema_version": WORKFLOW_BOARD_SCHEMA_VERSION,
        "kind": "workflow_card",
        "id": _text(card_id, "card"),
        "title": _text(title, "Untitled"),
        "subtitle": _text(subtitle),
        "status": normalized_status,
        "column": column_for_status(normalized_status),
        "source": _text(source, "manual"),
        "payload": dict(payload or {}),
        "actions": action_list,
        "action_count": len(action_list),
        "blocked": column_for_status(normalized_status) == "blocked",
        "ready": column_for_status(normalized_status) == "ready",
    }


def build_workflow_board(cards: Iterable[Mapping[str, Any]], *, title: str = "Workflow board") -> dict[str, object]:
    normalized_cards = [dict(card) for card in cards]
    columns = [
        {
            "id": column_id,
            "title": column_id.replace("_", " ").title(),
            "cards": [card for card in normalized_cards if _text(card.get("column")) == column_id],
        }
        for column_id in DEFAULT_COLUMNS
    ]
    return {
        "schema_version": WORKFLOW_BOARD_SCHEMA_VERSION,
        "kind": "workflow_board",
        "title": title,
        "column_order": list(DEFAULT_COLUMNS),
        "columns": columns,
        "cards": normalized_cards,
        "summary": {
            "card_count": len(normalized_cards),
            "ready_count": sum(1 for card in normalized_cards if _bool(card.get("ready"))),
            "blocked_count": sum(1 for card in normalized_cards if _bool(card.get("blocked"))),
            "review_count": sum(1 for card in normalized_cards if _text(card.get("column")) == "review"),
        },
    }


__all__ = [
    "WORKFLOW_BOARD_SCHEMA_VERSION",
    "DEFAULT_COLUMNS",
    "build_workflow_board",
    "build_workflow_card",
    "column_for_status",
    "normalize_workflow_status",
]
