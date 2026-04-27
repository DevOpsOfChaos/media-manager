from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .gui_qt_runtime_smoke_component_specs import build_qt_runtime_smoke_component_specs, lookup_qt_runtime_smoke_component

QT_RUNTIME_SMOKE_WIDGET_TREE_SCHEMA_VERSION = "1.0"


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: object) -> list[Any]:
    return value if isinstance(value, list) else []


def _safe_id(value: object, fallback: str = "node") -> str:
    text = str(value or fallback).strip().lower().replace("_", "-").replace(" ", "-")
    chars: list[str] = []
    last_dash = False
    for char in text:
        if char.isalnum():
            chars.append(char)
            last_dash = False
        elif not last_dash:
            chars.append("-")
            last_dash = True
    return "".join(chars).strip("-") or fallback


def _item_node(section_id: str, item: Mapping[str, Any], index: int) -> dict[str, object]:
    item_id = _safe_id(item.get("id") or item.get("row_id") or item.get("check_id") or f"item-{index + 1}")
    return {
        "id": f"{section_id}-{item_id}",
        "component": "MetricCard",
        "role": "item",
        "qt_widget": "QFrame",
        "layout": "QVBoxLayout",
        "props": dict(item),
        "children": [],
        "child_count": 0,
        "sensitive": bool(item.get("sensitive")),
        "executes_immediately": False,
    }


def build_qt_runtime_smoke_widget_tree(visible_surface: Mapping[str, Any]) -> dict[str, object]:
    visible_plan = _mapping(visible_surface.get("visible_plan") or visible_surface)
    specs = build_qt_runtime_smoke_component_specs()
    sections = [section for section in _list(visible_plan.get("sections")) if isinstance(section, Mapping)]
    section_nodes: list[dict[str, object]] = []
    unsupported: list[str] = []
    for index, section in enumerate(sections):
        section_id = _safe_id(section.get("id"), f"section-{index + 1}")
        component = str(section.get("component") or "QWidget")
        spec = lookup_qt_runtime_smoke_component(component, specs)
        if not spec.get("supported"):
            unsupported.append(component)
        item_nodes = [_item_node(section_id, item, item_index) for item_index, item in enumerate(_list(section.get("items"))) if isinstance(item, Mapping)]
        section_nodes.append(
            {
                "id": section_id,
                "component": component,
                "role": spec.get("role"),
                "qt_widget": spec.get("qt_widget"),
                "layout": spec.get("layout"),
                "props": {"title": section.get("title"), **dict(_mapping(section.get("props")))},
                "children": item_nodes,
                "child_count": len(item_nodes),
                "sensitive": bool(_mapping(section.get("props")).get("contains_sensitive_people_data_possible")),
                "executes_immediately": False,
            }
        )
    root = {
        "id": "runtime-smoke-root",
        "component": "RuntimeSmokePage",
        "role": "page",
        "qt_widget": "QWidget",
        "layout": "QVBoxLayout",
        "props": {"page_id": visible_plan.get("page_id"), "title": visible_plan.get("title"), "subtitle": visible_plan.get("subtitle")},
        "children": section_nodes,
        "child_count": len(section_nodes),
        "sensitive": bool(_mapping(visible_plan.get("summary")).get("contains_sensitive_people_data_possible")),
        "executes_immediately": False,
    }
    item_count = sum(len(_list(node.get("children"))) for node in section_nodes)
    return {
        "schema_version": QT_RUNTIME_SMOKE_WIDGET_TREE_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_widget_tree",
        "page_id": visible_plan.get("page_id"),
        "root": root,
        "component_specs": specs,
        "summary": {
            "node_count": 1 + len(section_nodes) + item_count,
            "section_count": len(section_nodes),
            "item_node_count": item_count,
            "unsupported_components": sorted(set(unsupported)),
            "unsupported_component_count": len(set(unsupported)),
            "sensitive_node_count": sum(1 for node in section_nodes if node.get("sensitive")) + (1 if root.get("sensitive") else 0),
            "executable_node_count": 0,
        },
        "capabilities": {"requires_pyside6": False, "opens_window": False, "headless_testable": True, "executes_commands": False, "local_only": True},
    }


__all__ = ["QT_RUNTIME_SMOKE_WIDGET_TREE_SCHEMA_VERSION", "build_qt_runtime_smoke_widget_tree"]
