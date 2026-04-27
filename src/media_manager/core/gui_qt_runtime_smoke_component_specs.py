from __future__ import annotations

from collections.abc import Mapping
from typing import Any

QT_RUNTIME_SMOKE_COMPONENT_SPECS_SCHEMA_VERSION = "1.0"

_COMPONENTS: dict[str, dict[str, object]] = {
    "StatusBanner": {"qt_widget": "QFrame", "layout": "QVBoxLayout", "role": "status", "supports_items": False},
    "DataTable": {"qt_widget": "QTableWidget", "layout": "table", "role": "table", "supports_items": True},
    "DetailPanel": {"qt_widget": "QFrame", "layout": "QVBoxLayout", "role": "group", "supports_items": False},
    "ActionBar": {"qt_widget": "QWidget", "layout": "QHBoxLayout", "role": "toolbar", "supports_items": True},
    "MetricCard": {"qt_widget": "QFrame", "layout": "QVBoxLayout", "role": "group", "supports_items": False},
    "Text": {"qt_widget": "QLabel", "layout": "none", "role": "text", "supports_items": False},
}


def build_qt_runtime_smoke_component_specs() -> dict[str, object]:
    return {
        "schema_version": QT_RUNTIME_SMOKE_COMPONENT_SPECS_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_component_specs",
        "components": {name: dict(spec) for name, spec in sorted(_COMPONENTS.items())},
        "summary": {"component_count": len(_COMPONENTS), "requires_pyside6": False, "opens_window": False},
        "capabilities": {"requires_pyside6": False, "opens_window": False, "headless_testable": True, "executes_commands": False, "local_only": True},
    }


def lookup_qt_runtime_smoke_component(component: str, specs: Mapping[str, Any] | None = None) -> dict[str, object]:
    catalog = specs if isinstance(specs, Mapping) else build_qt_runtime_smoke_component_specs()
    components = catalog.get("components") if isinstance(catalog.get("components"), Mapping) else {}
    payload = components.get(component) if isinstance(components, Mapping) else None
    if isinstance(payload, Mapping):
        return {"component": component, "supported": True, **dict(payload)}
    return {"component": component, "supported": False, "qt_widget": "QWidget", "layout": "QVBoxLayout", "role": "group", "supports_items": True}


__all__ = [
    "QT_RUNTIME_SMOKE_COMPONENT_SPECS_SCHEMA_VERSION",
    "build_qt_runtime_smoke_component_specs",
    "lookup_qt_runtime_smoke_component",
]
