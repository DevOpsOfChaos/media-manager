from __future__ import annotations

from collections.abc import Mapping
from typing import Any

QT_RUNTIME_SMOKE_SHELL_MODEL_ADAPTER_SCHEMA_VERSION = "1.0"


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: object) -> list[Any]:
    return value if isinstance(value, list) else []


def _nav_id(item: Mapping[str, Any]) -> str:
    return str(item.get("id") or item.get("page_id") or "")


def apply_guarded_qt_runtime_smoke_to_shell_model(
    shell_model: Mapping[str, Any],
    guarded_integration: Mapping[str, Any],
    *,
    activate: bool = False,
) -> dict[str, object]:
    """Inject Runtime Smoke route metadata into the existing shell model.

    The adapter mutates only the returned copy. It does not import Qt, open a
    window, or execute any command handlers.
    """

    payload: dict[str, object] = dict(shell_model)
    page_handoff = _mapping(guarded_integration.get("page_handoff"))
    nav_item = dict(_mapping(page_handoff.get("navigation_item")))
    nav_item.setdefault("id", "runtime-smoke")
    nav_item.setdefault("page_id", "runtime-smoke")
    nav_item.setdefault("label", "Runtime Smoke")
    nav_item.setdefault("icon", "activity")
    nav_item["active"] = bool(activate)
    navigation = [dict(item) for item in _list(shell_model.get("navigation")) if isinstance(item, Mapping) and _nav_id(item) != "runtime-smoke"]
    if activate:
        for item in navigation:
            item["active"] = False
    navigation.append(nav_item)
    payload["navigation"] = navigation
    if activate:
        payload["active_page_id"] = "runtime-smoke"
        payload["page"] = guarded_integration.get("page_model")
    palette = dict(_mapping(shell_model.get("command_palette")))
    existing_items = [dict(item) for item in _list(palette.get("items")) if isinstance(item, Mapping)]
    runtime_items = [
        dict(item)
        for item in _list(_mapping(guarded_integration.get("command_palette_binding")).get("items"))
        if isinstance(item, Mapping)
    ]
    seen = {str(item.get("id")) for item in existing_items}
    palette["items"] = [*existing_items, *(item for item in runtime_items if str(item.get("id")) not in seen)]
    payload["command_palette"] = palette
    payload["runtime_smoke"] = {
        "schema_version": QT_RUNTIME_SMOKE_SHELL_MODEL_ADAPTER_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_shell_model_attachment",
        "page_id": "runtime-smoke",
        "guarded_integration": guarded_integration,
        "active": bool(activate),
        "summary": dict(_mapping(guarded_integration.get("summary"))),
    }
    status_bar = dict(_mapping(shell_model.get("status_bar")))
    if activate:
        manual = _mapping(guarded_integration.get("manual_readiness"))
        status_bar["text"] = manual.get("recommended_next_step") or "Runtime Smoke ready for review."
    payload["status_bar"] = status_bar
    return payload


def summarize_runtime_smoke_shell_attachment(shell_model: Mapping[str, Any]) -> dict[str, object]:
    attachment = _mapping(shell_model.get("runtime_smoke"))
    summary = _mapping(attachment.get("summary"))
    return {
        "schema_version": QT_RUNTIME_SMOKE_SHELL_MODEL_ADAPTER_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_shell_attachment_summary",
        "attached": bool(attachment),
        "active": bool(attachment.get("active")),
        "ready_for_shell_route": bool(summary.get("ready_for_shell_route")),
        "navigation_count": len(_list(shell_model.get("navigation"))),
        "command_palette_item_count": len(_list(_mapping(shell_model.get("command_palette")).get("items"))),
        "opens_window": False,
        "executes_commands": False,
        "local_only": True,
    }


__all__ = [
    "QT_RUNTIME_SMOKE_SHELL_MODEL_ADAPTER_SCHEMA_VERSION",
    "apply_guarded_qt_runtime_smoke_to_shell_model",
    "summarize_runtime_smoke_shell_attachment",
]
