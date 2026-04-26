from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .gui_render_runtime import flatten_widget_tree

QT_WIDGET_PLAN_SCHEMA_VERSION = "1.0"

_QT_CLASS_BY_TYPE = {
    "card": "QFrame",
    "metric_card": "QFrame",
    "section": "QFrame",
    "text": "QLabel",
    "label": "QLabel",
    "button": "QPushButton",
    "table": "QTableWidget",
    "face_card": "QFrame",
    "grid": "QWidget",
    "dashboard_page": "QWidget",
    "people_review_page": "QWidget",
}


def qt_class_for_widget_type(widget_type: str) -> str:
    return _QT_CLASS_BY_TYPE.get(str(widget_type), "QWidget")


def build_qt_widget_plan(render_contract: Mapping[str, Any]) -> dict[str, object]:
    root = render_contract.get("root") or render_contract.get("render_spec") or render_contract.get("page") or render_contract
    widgets = flatten_widget_tree(root if isinstance(root, Mapping) else {})
    plan_items: list[dict[str, object]] = []
    for item in widgets:
        widget = item.get("widget") if isinstance(item.get("widget"), Mapping) else {}
        widget_type = str(item.get("type") or "unknown")
        plan_items.append(
            {
                "id": item.get("id"),
                "type": widget_type,
                "qt_class": qt_class_for_widget_type(widget_type),
                "parent_id": item.get("parent_id"),
                "object_name": widget.get("object_name") or widget.get("id") or item.get("id"),
                "text": widget.get("title") or widget.get("label") or widget.get("text"),
            }
        )
    return {
        "schema_version": QT_WIDGET_PLAN_SCHEMA_VERSION,
        "kind": "qt_widget_plan",
        "widget_count": len(plan_items),
        "widgets": plan_items,
        "unsupported_count": sum(1 for item in plan_items if item["qt_class"] == "QWidget" and item["type"] not in {"grid", "dashboard_page", "people_review_page"}),
    }


def validate_qt_widget_plan(plan: Mapping[str, Any]) -> dict[str, object]:
    widgets = plan.get("widgets") if isinstance(plan.get("widgets"), list) else []
    ids = [str(item.get("id")) for item in widgets if isinstance(item, Mapping) and item.get("id")]
    duplicate_ids = sorted({item for item in ids if ids.count(item) > 1})
    return {
        "schema_version": QT_WIDGET_PLAN_SCHEMA_VERSION,
        "valid": not duplicate_ids,
        "widget_count": len(widgets),
        "duplicate_ids": duplicate_ids,
        "unsupported_count": plan.get("unsupported_count", 0),
    }


__all__ = ["QT_WIDGET_PLAN_SCHEMA_VERSION", "build_qt_widget_plan", "qt_class_for_widget_type", "validate_qt_widget_plan"]
