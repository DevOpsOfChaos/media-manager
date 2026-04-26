from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

COMPONENT_REGISTRY_SCHEMA_VERSION = "1.0"

_DEFAULT_COMPONENTS = {
    "action_bar": {"qt_widget": "QFrame", "region": "actions"},
    "badge": {"qt_widget": "QLabel", "region": "inline"},
    "button": {"qt_widget": "QPushButton", "region": "actions"},
    "card": {"qt_widget": "QFrame", "region": "content"},
    "card_grid": {"qt_widget": "QGridLayout", "region": "content"},
    "empty_state": {"qt_widget": "QFrame", "region": "content"},
    "face_card": {"qt_widget": "QFrame", "region": "content"},
    "footer": {"qt_widget": "QStatusBar", "region": "footer"},
    "hero": {"qt_widget": "QFrame", "region": "hero"},
    "image": {"qt_widget": "QLabel", "region": "content"},
    "list": {"qt_widget": "QListWidget", "region": "content"},
    "metric": {"qt_widget": "QLabel", "region": "content"},
    "navigation": {"qt_widget": "QFrame", "region": "sidebar"},
    "panel": {"qt_widget": "QFrame", "region": "content"},
    "search": {"qt_widget": "QLineEdit", "region": "toolbar"},
    "section": {"qt_widget": "QFrame", "region": "content"},
    "table": {"qt_widget": "QTableWidget", "region": "content"},
    "text": {"qt_widget": "QLabel", "region": "content"},
    "timeline": {"qt_widget": "QFrame", "region": "content"},
}


def build_component_registry(extra_components: Iterable[Mapping[str, Any]] = ()) -> dict[str, object]:
    components = {
        key: {"component": key, **value, "available": True}
        for key, value in sorted(_DEFAULT_COMPONENTS.items())
    }
    for item in extra_components:
        if not isinstance(item, Mapping):
            continue
        component = str(item.get("component") or item.get("widget_type") or "").strip()
        if not component:
            continue
        payload = dict(item)
        payload["component"] = component
        payload.setdefault("available", True)
        components[component] = payload
    return {
        "schema_version": COMPONENT_REGISTRY_SCHEMA_VERSION,
        "kind": "gui_component_registry",
        "component_count": len(components),
        "components": components,
    }


def lookup_component(registry: Mapping[str, Any], widget_type: str) -> dict[str, object]:
    components = registry.get("components") if isinstance(registry.get("components"), Mapping) else {}
    item = components.get(widget_type) if isinstance(components, Mapping) else None
    if isinstance(item, Mapping):
        return dict(item)
    return {"component": widget_type, "available": False, "qt_widget": None, "region": "content"}


def validate_widget_types(registry: Mapping[str, Any], widget_tree: Mapping[str, Any]) -> dict[str, object]:
    components = registry.get("components") if isinstance(registry.get("components"), Mapping) else {}
    known = set(components.keys()) if isinstance(components, Mapping) else set()
    missing: list[str] = []

    def visit(item: object) -> None:
        if not isinstance(item, Mapping):
            return
        widget_type = str(item.get("widget_type") or "")
        if widget_type and widget_type not in known:
            missing.append(widget_type)
        children = item.get("children")
        if isinstance(children, list):
            for child in children:
                visit(child)
        slots = item.get("slots")
        if isinstance(slots, Mapping):
            for value in slots.values():
                if isinstance(value, Mapping):
                    visit(value)
                elif isinstance(value, list):
                    for child in value:
                        visit(child)

    visit(widget_tree)
    unique_missing = sorted(set(missing))
    return {
        "schema_version": COMPONENT_REGISTRY_SCHEMA_VERSION,
        "valid": not unique_missing,
        "missing_widget_types": unique_missing,
        "missing_count": len(unique_missing),
    }


__all__ = [
    "COMPONENT_REGISTRY_SCHEMA_VERSION",
    "build_component_registry",
    "lookup_component",
    "validate_widget_types",
]
