from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

VALIDATION_PANEL_SCHEMA_VERSION = "1.0"


def build_validation_message(code: str, message: str, *, severity: str = "info", target: str | None = None) -> dict[str, object]:
    return {
        "schema_version": VALIDATION_PANEL_SCHEMA_VERSION,
        "code": code,
        "message": message,
        "severity": severity,
        "target": target,
    }


def build_validation_panel(messages: Iterable[Mapping[str, Any]]) -> dict[str, object]:
    items = [dict(item) for item in messages]
    return {
        "schema_version": VALIDATION_PANEL_SCHEMA_VERSION,
        "kind": "validation_panel",
        "messages": items,
        "message_count": len(items),
        "error_count": sum(1 for item in items if item.get("severity") == "error"),
        "warning_count": sum(1 for item in items if item.get("severity") == "warning"),
    }


def validation_panel_from_status(payload: Mapping[str, Any]) -> dict[str, object]:
    messages = []
    if payload.get("empty_state"):
        messages.append(build_validation_message("empty_state", str(payload.get("empty_state")), severity="info"))
    overview = payload.get("overview") if isinstance(payload.get("overview"), Mapping) else {}
    if overview.get("needs_name_group_count"):
        messages.append(build_validation_message("people_needs_name", f"{overview.get('needs_name_group_count')} groups need a name.", severity="warning"))
    if overview.get("groups_truncated"):
        messages.append(build_validation_message("truncated", "Only a subset of groups is shown.", severity="warning"))
    return build_validation_panel(messages)


__all__ = ["VALIDATION_PANEL_SCHEMA_VERSION", "build_validation_message", "build_validation_panel", "validation_panel_from_status"]
