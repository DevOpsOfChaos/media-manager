from __future__ import annotations
from collections.abc import Mapping
from typing import Any
QT_RUNTIME_SMOKE_SHELL_NAVIGATION_PATCH_SCHEMA_VERSION = "1.0"
def _list(value: object) -> list[Any]: return value if isinstance(value, list) else []
def build_qt_runtime_smoke_shell_navigation_patch(shell_registration: Mapping[str, Any], *, existing_items: list[Mapping[str, Any]] | None = None) -> dict[str, object]:
    nav = dict(shell_registration.get("navigation_item")) if isinstance(shell_registration.get("navigation_item"), Mapping) else {}
    item_id = str(nav.get("id") or shell_registration.get("route_id") or "runtime-smoke")
    items = [dict(item) for item in (existing_items or []) if isinstance(item, Mapping)]
    before_count = len(items)
    items = [item for item in items if item.get("id") != item_id and item.get("page_id") != shell_registration.get("page_id")]
    patch_item = {**nav, "id": item_id, "page_id": shell_registration.get("page_id"), "section_id": shell_registration.get("section_id"), "enabled": bool(shell_registration.get("enabled")), "visible": bool(shell_registration.get("visible", True)), "executes_immediately": False}
    items.append(patch_item)
    return {"schema_version": QT_RUNTIME_SMOKE_SHELL_NAVIGATION_PATCH_SCHEMA_VERSION, "kind": "qt_runtime_smoke_shell_navigation_patch", "operation": "upsert_navigation_item", "item": patch_item, "items": items, "summary": {"before_count": before_count, "after_count": len(items), "replaced_existing": before_count == len(items), "runtime_smoke_item_count": sum(1 for item in items if item.get("id") == item_id), "enabled": bool(patch_item.get("enabled")), "opens_window": False, "executes_commands": False}, "capabilities": {"requires_pyside6": False, "opens_window": False, "headless_testable": True, "executes_commands": False, "local_only": True}}
def collect_qt_runtime_smoke_navigation_ids(patch: Mapping[str, Any]) -> list[str]: return [str(item.get("id")) for item in _list(patch.get("items")) if isinstance(item, Mapping)]
__all__ = ["QT_RUNTIME_SMOKE_SHELL_NAVIGATION_PATCH_SCHEMA_VERSION", "build_qt_runtime_smoke_shell_navigation_patch", "collect_qt_runtime_smoke_navigation_ids"]
