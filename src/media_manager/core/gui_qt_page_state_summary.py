from __future__ import annotations

from collections.abc import Mapping
from typing import Any

PAGE_STATE_SUMMARY_SCHEMA_VERSION = "1.0"


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: object) -> list[Any]:
    return value if isinstance(value, list) else []


def build_qt_page_state_summary(page_model: Mapping[str, Any]) -> dict[str, object]:
    page_id = str(page_model.get("page_id") or "unknown")
    kind = str(page_model.get("kind") or "unknown")
    groups = _list(page_model.get("groups"))
    rows = _list(page_model.get("rows"))
    cards = _list(page_model.get("cards"))
    validation = _mapping(page_model.get("validation"))
    empty_state = page_model.get("empty_state") is not None
    return {
        "schema_version": PAGE_STATE_SUMMARY_SCHEMA_VERSION,
        "kind": "qt_page_state_summary",
        "page_id": page_id,
        "page_kind": kind,
        "title": page_model.get("title"),
        "layout": page_model.get("layout"),
        "has_empty_state": empty_state,
        "group_count": len(groups),
        "row_count": len(rows),
        "card_count": len(cards),
        "validation_message_count": int(validation.get("message_count") or 0),
        "needs_attention": bool(empty_state or int(validation.get("error_count") or 0) > 0 or int(validation.get("warning_count") or 0) > 0),
    }


def build_qt_shell_state_summary(shell_model: Mapping[str, Any]) -> dict[str, object]:
    page = _mapping(shell_model.get("page"))
    nav = _list(shell_model.get("navigation"))
    capabilities = _mapping(shell_model.get("capabilities"))
    return {
        "schema_version": PAGE_STATE_SUMMARY_SCHEMA_VERSION,
        "kind": "qt_shell_state_summary",
        "active_page_id": shell_model.get("active_page_id"),
        "language": shell_model.get("language"),
        "theme": _mapping(shell_model.get("theme")).get("theme"),
        "navigation_count": len(nav),
        "enabled_navigation_count": sum(1 for item in nav if _mapping(item).get("enabled", True)),
        "page_summary": build_qt_page_state_summary(page),
        "qt_shell": bool(capabilities.get("qt_shell")),
        "executes_commands": bool(capabilities.get("executes_commands")),
    }


__all__ = ["PAGE_STATE_SUMMARY_SCHEMA_VERSION", "build_qt_page_state_summary", "build_qt_shell_state_summary"]
