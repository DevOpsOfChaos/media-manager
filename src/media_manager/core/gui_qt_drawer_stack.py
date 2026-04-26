from __future__ import annotations

from collections.abc import Mapping
from typing import Any

DRAWER_STACK_SCHEMA_VERSION = "1.0"


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _drawer(drawer_id: str, title: str, *, open_: bool = False, item_count: int = 0, severity: str = "info") -> dict[str, object]:
    return {
        "schema_version": DRAWER_STACK_SCHEMA_VERSION,
        "kind": "drawer",
        "id": drawer_id,
        "title": title,
        "open": bool(open_),
        "item_count": int(item_count),
        "severity": severity,
    }


def build_drawer_stack(shell_model: Mapping[str, Any]) -> dict[str, object]:
    notifications = _as_mapping(shell_model.get("notifications") or shell_model.get("notification_center"))
    diagnostics = _as_mapping(shell_model.get("diagnostics"))
    command_palette = _as_mapping(shell_model.get("command_palette"))
    onboarding = _as_mapping(shell_model.get("onboarding"))
    drawers = [
        _drawer("notifications", "Notifications", item_count=int(notifications.get("message_count") or notifications.get("item_count") or 0), severity="warning" if notifications.get("error_count") else "info"),
        _drawer("diagnostics", "Diagnostics", item_count=int(diagnostics.get("problem_count") or diagnostics.get("item_count") or 0), severity="error" if diagnostics.get("error_count") else "info"),
        _drawer("command_palette", str(command_palette.get("title") or "Command palette"), item_count=len(_as_list(command_palette.get("items"))) or len(_as_list(command_palette.get("commands")))),
        _drawer("onboarding", str(onboarding.get("title") or "Onboarding"), open_=not bool(onboarding.get("dismissed", True)), item_count=len(_as_list(onboarding.get("steps")))),
    ]
    return {
        "schema_version": DRAWER_STACK_SCHEMA_VERSION,
        "kind": "drawer_stack",
        "drawers": drawers,
        "drawer_count": len(drawers),
        "open_drawer_count": sum(1 for item in drawers if item.get("open")),
        "attention_count": sum(1 for item in drawers if item.get("severity") in {"warning", "error"} and int(item.get("item_count", 0)) > 0),
    }


__all__ = ["DRAWER_STACK_SCHEMA_VERSION", "build_drawer_stack"]
