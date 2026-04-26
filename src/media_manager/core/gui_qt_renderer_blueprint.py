from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

BLUEPRINT_SCHEMA_VERSION = "1.0"

def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}

def _list(value: object) -> list[Any]:
    return value if isinstance(value, list) else []

def _text(value: object, fallback: str = "") -> str:
    return str(value) if value is not None else fallback

def _widget_node(widget_type: str, *, widget_id: str, props: Mapping[str, Any] | None = None, children: Sequence[Mapping[str, Any]] = ()) -> dict[str, object]:
    return {
        "widget_id": widget_id,
        "widget_type": widget_type,
        "props": dict(props or {}),
        "children": [dict(child) for child in children],
    }

def _navigation_blueprint(navigation: Sequence[Any]) -> dict[str, object]:
    buttons = []
    for index, raw in enumerate(navigation):
        item = _mapping(raw)
        page_id = _text(item.get("id") or item.get("page_id"))
        if not page_id:
            continue
        buttons.append(
            _widget_node(
                "QPushButton",
                widget_id=f"nav.{page_id}",
                props={
                    "text": _text(item.get("label"), page_id),
                    "checkable": True,
                    "checked": bool(item.get("active")),
                    "enabled": bool(item.get("enabled", True)),
                    "target_page_id": page_id,
                    "shortcut": item.get("shortcut") or f"Ctrl+{index + 1}",
                    "object_name": "SidebarButton",
                },
            )
        )
    return _widget_node(
        "QFrame",
        widget_id="sidebar",
        props={"object_name": "Sidebar", "role": "navigation"},
        children=buttons,
    )

def _page_blueprint(page: Mapping[str, Any]) -> dict[str, object]:
    kind = _text(page.get("kind"), "placeholder_page")
    page_id = _text(page.get("page_id"), "unknown")
    title = _text(page.get("title"), page_id)
    content_children: list[dict[str, object]] = [
        _widget_node("QLabel", widget_id=f"{page_id}.title", props={"text": title, "object_name": "PageTitle"})
    ]
    if kind == "dashboard_page":
        for idx, raw_card in enumerate(_list(page.get("cards"))):
            card = _mapping(raw_card)
            content_children.append(
                _widget_node(
                    "QFrame",
                    widget_id=f"{page_id}.card.{card.get('id', idx)}",
                    props={
                        "component": "metric_card",
                        "title": card.get("title"),
                        "subtitle": card.get("subtitle"),
                        "metrics": dict(_mapping(card.get("metrics"))),
                    },
                )
            )
    elif kind == "people_review_page":
        content_children.append(
            _widget_node(
                "QSplitter",
                widget_id="people-review.master-detail",
                props={"orientation": "horizontal", "component": "people_review_split"},
                children=[
                    _widget_node("QListWidget", widget_id="people-review.groups", props={"count": len(_list(page.get("groups")))}),
                    _widget_node("QScrollArea", widget_id="people-review.detail", props={"selected_group_id": page.get("selected_group_id")}),
                ],
            )
        )
    elif kind in {"table_page", "profiles_page"}:
        content_children.append(
            _widget_node(
                "QTableWidget",
                widget_id=f"{page_id}.table",
                props={"columns": list(_list(page.get("columns"))), "row_count": len(_list(page.get("rows")))},
            )
        )
    else:
        content_children.append(
            _widget_node("QLabel", widget_id=f"{page_id}.empty", props={"text": _text(_mapping(page.get("empty_state")).get("title"), "Ready.")})
        )
    return _widget_node(
        "QScrollArea",
        widget_id=f"page.{page_id}",
        props={"page_id": page_id, "kind": kind, "widget_resizable": True},
        children=content_children,
    )

def build_qt_renderer_blueprint(shell_model: Mapping[str, Any]) -> dict[str, object]:
    """Build a declarative Qt widget tree blueprint without importing PySide6."""
    page = _mapping(shell_model.get("page"))
    window = _mapping(shell_model.get("window"))
    navigation = _list(shell_model.get("navigation"))
    root_children = [
        _navigation_blueprint(navigation),
        _page_blueprint(page),
    ]
    blueprint = {
        "schema_version": BLUEPRINT_SCHEMA_VERSION,
        "kind": "qt_renderer_blueprint",
        "window": {
            "title": window.get("title") or "Media Manager",
            "width": int(window.get("width", 1440) or 1440),
            "height": int(window.get("height", 940) or 940),
            "minimum_width": int(window.get("minimum_width", 1100) or 1100),
            "minimum_height": int(window.get("minimum_height", 740) or 740),
        },
        "root": _widget_node("QMainWindow", widget_id="main_window", props={"object_name": "MainWindow"}, children=[
            _widget_node("QWidget", widget_id="central_widget", props={"layout": "QHBoxLayout"}, children=root_children)
        ]),
        "active_page_id": shell_model.get("active_page_id"),
        "widget_summary": summarize_blueprint_widgets(root_children),
    }
    return blueprint

def _walk_widgets(nodes: Sequence[Mapping[str, Any]]) -> list[Mapping[str, Any]]:
    flattened: list[Mapping[str, Any]] = []
    for node in nodes:
        flattened.append(node)
        flattened.extend(_walk_widgets([child for child in _list(node.get("children")) if isinstance(child, Mapping)]))
    return flattened

def summarize_blueprint_widgets(nodes: Sequence[Mapping[str, Any]]) -> dict[str, object]:
    counts: dict[str, int] = {}
    for node in _walk_widgets(nodes):
        kind = _text(node.get("widget_type"), "unknown")
        counts[kind] = counts.get(kind, 0) + 1
    return {"widget_count": sum(counts.values()), "widget_type_summary": dict(sorted(counts.items()))}

__all__ = ["BLUEPRINT_SCHEMA_VERSION", "build_qt_renderer_blueprint", "summarize_blueprint_widgets"]
