from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .gui_qt_view_action_registry import build_view_action_registry

QT_RUNTIME_SMOKE_SHELL_ACTION_REGISTRY_SCHEMA_VERSION = "1.0"


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: object) -> list[Any]:
    return value if isinstance(value, list) else []


def build_qt_runtime_smoke_shell_action_registry(
    *,
    page_model: Mapping[str, Any],
    shell_bundle: Mapping[str, Any],
    command_palette_binding: Mapping[str, Any],
) -> dict[str, object]:
    """Merge Runtime Smoke page, navigation, and command-palette actions."""

    registration = _mapping(shell_bundle.get("shell_registration"))
    navigation = [
        {
            "id": registration.get("page_id") or "runtime-smoke",
            "label": registration.get("label") or "Runtime Smoke",
            "enabled": bool(registration.get("enabled")),
            "page_id": registration.get("page_id") or "runtime-smoke",
            "shortcut": "Ctrl+Shift+R",
        }
    ]
    command_palette = {"items": _list(command_palette_binding.get("items"))}
    registry = build_view_action_registry(
        page_model=page_model,
        page_actions=[item for item in _list(page_model.get("actions")) if isinstance(item, Mapping)],
        navigation=navigation,
        command_palette=command_palette,
    )
    return {
        "schema_version": QT_RUNTIME_SMOKE_SHELL_ACTION_REGISTRY_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_shell_action_registry",
        "page_id": "runtime-smoke",
        "registry": registry,
        "actions": registry["actions"],
        "summary": {
            "action_count": registry["action_count"],
            "enabled_action_count": registry["enabled_count"],
            "confirmation_action_count": registry["confirmation_count"],
            "immediate_execution_count": sum(1 for action in registry["actions"] if action.get("executes_immediately")),
        },
        "capabilities": {
            "requires_pyside6": False,
            "opens_window": False,
            "headless_testable": True,
            "executes_commands": False,
            "local_only": True,
        },
    }


__all__ = [
    "QT_RUNTIME_SMOKE_SHELL_ACTION_REGISTRY_SCHEMA_VERSION",
    "build_qt_runtime_smoke_shell_action_registry",
]
