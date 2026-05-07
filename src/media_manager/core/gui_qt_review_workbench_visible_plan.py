from __future__ import annotations

from collections.abc import Mapping
from typing import Any

REVIEW_WORKBENCH_VISIBLE_PLAN_SCHEMA_VERSION = "1.0"


def _as_mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _as_list(value: object) -> list[Any]:
    return value if isinstance(value, list) else []


def _component_section(component: Mapping[str, Any]) -> dict[str, object]:
    props = _as_mapping(component.get("props"))
    return {
        "section_id": str(component.get("component_id") or "review-workbench-component"),
        "kind": "qt_review_workbench_component_section",
        "component_type": str(component.get("component_type") or "ReviewWorkbenchComponent"),
        "role": str(component.get("role") or "component"),
        "title": str(props.get("title") or props.get("headline") or component.get("component_type") or "Review Workbench"),
        "sensitive": bool(component.get("sensitive")),
        "props": dict(props),
    }


def build_qt_review_workbench_visible_plan(page_model: Mapping[str, Any]) -> dict[str, object]:
    adapter = _as_mapping(page_model.get("qt_adapter_package"))
    widget_binding_plan = _as_mapping(page_model.get("qt_widget_binding_plan"))
    components = [item for item in _as_list(adapter.get("components")) if isinstance(item, Mapping)]
    route_intents = [dict(item) for item in _as_list(adapter.get("route_intents")) if isinstance(item, Mapping)]
    widget_bindings = [dict(item) for item in _as_list(widget_binding_plan.get("widget_bindings")) if isinstance(item, Mapping)]
    sections = [_component_section(component) for component in components]
    section_ids = {section.get("section_id") for section in sections}
    bound_component_ids = {binding.get("component_id") for binding in widget_bindings}
    unbound_sections = sorted(str(section_id) for section_id in section_ids if section_id not in bound_component_ids)
    return {
        "schema_version": REVIEW_WORKBENCH_VISIBLE_PLAN_SCHEMA_VERSION,
        "kind": "qt_review_workbench_visible_plan",
        "page_id": "review-workbench",
        "layout": "review_workbench_table_detail",
        "sections": sections,
        "route_intents": route_intents,
        "widget_binding_plan": dict(widget_binding_plan),
        "widget_bindings": widget_bindings,
        "unbound_sections": unbound_sections,
        "summary": {
            "component_count": len(components),
            "section_count": len(sections),
            "widget_binding_count": len(widget_bindings),
            "route_intent_count": len(route_intents),
            "sensitive_section_count": sum(1 for section in sections if section.get("sensitive")),
            "unbound_section_count": len(unbound_sections),
            "ready_for_qt": bool(adapter.get("ready")) and bool(widget_binding_plan.get("ready")) and bool(sections) and not unbound_sections,
        },
        "ready_for_qt": bool(adapter.get("ready")) and bool(widget_binding_plan.get("ready")) and bool(sections) and not unbound_sections,
    }


__all__ = ["REVIEW_WORKBENCH_VISIBLE_PLAN_SCHEMA_VERSION", "build_qt_review_workbench_visible_plan"]
