from __future__ import annotations

from collections.abc import Mapping
from typing import Any

TOP_BAR_SCHEMA_VERSION = "1.0"


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def build_top_bar_action(action_id: str, label: str, *, icon: str = "circle", enabled: bool = True, variant: str = "secondary") -> dict[str, object]:
    return {
        "schema_version": TOP_BAR_SCHEMA_VERSION,
        "kind": "top_bar_action",
        "id": str(action_id),
        "label": str(label),
        "icon": icon,
        "enabled": bool(enabled),
        "variant": variant,
    }


def build_top_bar_model(shell_model: Mapping[str, Any]) -> dict[str, object]:
    app = _as_mapping(shell_model.get("application"))
    page = _as_mapping(shell_model.get("page"))
    palette = _as_mapping(_as_mapping(shell_model.get("theme")).get("palette") or _as_mapping(shell_model.get("theme")).get("tokens"))
    actions = [
        build_top_bar_action("command_palette", "Command palette", icon="search"),
        build_top_bar_action("settings", "Settings", icon="settings"),
    ]
    page_actions = [item for item in _as_list(shell_model.get("page_actions")) if isinstance(item, Mapping)]
    for raw in page_actions[:2]:
        actions.append(
            build_top_bar_action(
                str(raw.get("id") or "page_action"),
                str(raw.get("label") or raw.get("id") or "Action"),
                icon=str(raw.get("icon") or "zap"),
                enabled=bool(raw.get("enabled", True)),
                variant=str(raw.get("variant") or "secondary"),
            )
        )
    return {
        "schema_version": TOP_BAR_SCHEMA_VERSION,
        "kind": "top_bar",
        "app_title": app.get("title") or "Media Manager",
        "page_title": page.get("title") or shell_model.get("active_page_id") or "Dashboard",
        "page_description": page.get("description"),
        "theme_accent": palette.get("accent"),
        "actions": actions,
        "action_count": len(actions),
    }


__all__ = ["TOP_BAR_SCHEMA_VERSION", "build_top_bar_action", "build_top_bar_model"]
