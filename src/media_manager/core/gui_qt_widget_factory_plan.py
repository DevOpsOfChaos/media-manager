from __future__ import annotations

from collections.abc import Mapping
from typing import Any

FACTORY_PLAN_SCHEMA_VERSION = "1.0"

DEFAULT_WIDGET_TYPE_MAP = {
    "window": "QMainWindow",
    "sidebar": "QFrame",
    "page": "QWidget",
    "section": "QFrame",
    "card": "QFrame",
    "text": "QLabel",
    "metric": "QLabel",
    "button": "QPushButton",
    "table": "QTableWidget",
    "image": "QLabel",
    "split": "QSplitter",
    "scroll": "QScrollArea",
    "toolbar": "QFrame",
    "status": "QStatusBar",
}


def _as_mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _as_list(value: object) -> list[Any]:
    return value if isinstance(value, list) else []


def _walk_widgets(widget: Mapping[str, Any], *, depth: int = 0) -> list[dict[str, object]]:
    widget_type = str(widget.get("type") or widget.get("widget_type") or "unknown")
    widget_id = str(widget.get("id") or f"anonymous-{depth}")
    rows = [
        {
            "id": widget_id,
            "type": widget_type,
            "qt_class": DEFAULT_WIDGET_TYPE_MAP.get(widget_type, "unsupported"),
            "depth": depth,
            "supported": widget_type in DEFAULT_WIDGET_TYPE_MAP,
        }
    ]
    for child in _as_list(widget.get("children")):
        if isinstance(child, Mapping):
            rows.extend(_walk_widgets(child, depth=depth + 1))
    return rows


def build_qt_widget_factory_plan(widget_tree: Mapping[str, Any]) -> dict[str, object]:
    """Build a declarative plan for converting widget-tree nodes into Qt classes.

    The plan does not import PySide6. It is safe to build in headless tests and
    can be used later by the real Qt renderer to decide which widget factory to call.
    """

    widgets = _walk_widgets(widget_tree)
    unsupported = [item for item in widgets if not item["supported"]]
    type_summary: dict[str, int] = {}
    for item in widgets:
        key = str(item["type"])
        type_summary[key] = type_summary.get(key, 0) + 1
    return {
        "schema_version": FACTORY_PLAN_SCHEMA_VERSION,
        "kind": "qt_widget_factory_plan",
        "root_id": widget_tree.get("id"),
        "widget_count": len(widgets),
        "supported_widget_count": len(widgets) - len(unsupported),
        "unsupported_widget_count": len(unsupported),
        "type_summary": dict(sorted(type_summary.items())),
        "widgets": widgets,
        "unsupported_widgets": unsupported,
        "ready_for_qt_renderer": not unsupported,
    }


def validate_qt_widget_factory_plan(plan: Mapping[str, Any]) -> dict[str, object]:
    unsupported = [item for item in _as_list(plan.get("unsupported_widgets")) if isinstance(item, Mapping)]
    problems = [f"Unsupported widget type: {item.get('type')} ({item.get('id')})" for item in unsupported]
    return {
        "valid": not problems,
        "problem_count": len(problems),
        "problems": problems,
        "ready_for_qt_renderer": bool(plan.get("ready_for_qt_renderer")) and not problems,
    }


__all__ = [
    "FACTORY_PLAN_SCHEMA_VERSION",
    "DEFAULT_WIDGET_TYPE_MAP",
    "build_qt_widget_factory_plan",
    "validate_qt_widget_factory_plan",
]
