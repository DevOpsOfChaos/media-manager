from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .gui_qt_dashboard_render_tree import build_dashboard_render_tree
from .gui_qt_people_review_render_tree import build_people_review_render_tree
from .gui_qt_render_tree import build_leaf_node, build_render_node, summarize_render_tree

SHELL_RENDER_TREE_SCHEMA_VERSION = "1.0"


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: object) -> list[Any]:
    return value if isinstance(value, list) else []


def _text(value: object, fallback: str = "") -> str:
    text = str(value).strip() if value is not None else ""
    return text or fallback


def _page_tree(page_plan: Mapping[str, Any]) -> Mapping[str, Any]:
    body = _mapping(page_plan.get("body"))
    body_kind = str(body.get("kind") or page_plan.get("page_kind") or "")
    if body_kind == "qt_dashboard_visible_plan" or page_plan.get("page_id") == "dashboard":
        return build_dashboard_render_tree(page_plan)
    if body_kind == "qt_people_review_visible_plan" or page_plan.get("page_id") == "people-review":
        return build_people_review_render_tree(page_plan)
    page_id = _text(page_plan.get("page_id"), "page")
    root = build_render_node(
        f"{page_id}-root",
        "GenericPage",
        role="page",
        props={
            "page_id": page_id,
            "page_kind": page_plan.get("page_kind"),
            "body_kind": body_kind,
            "ready_for_qt": bool(page_plan.get("ready_for_qt")),
        },
    )
    return {"schema_version": SHELL_RENDER_TREE_SCHEMA_VERSION, "kind": "qt_generic_page_render_tree", "page_id": page_id, "root": root, "summary": summarize_render_tree(root)}


def _navigation_tree(plan: Mapping[str, Any]) -> dict[str, object]:
    navigation = [item for item in _list(plan.get("navigation")) if isinstance(item, Mapping)]
    items = [
        build_leaf_node(
            f"nav-{item.get('id') or index + 1}",
            "NavigationItem",
            role="navigation_item",
            props={
                "page_id": item.get("id"),
                "label": item.get("label"),
                "active": bool(item.get("active")),
                "enabled": bool(item.get("enabled", True)),
                "shortcut": item.get("shortcut"),
            },
        )
        for index, item in enumerate(navigation)
    ]
    return build_render_node(
        "navigation-rail",
        "NavigationRail",
        role="navigation",
        props={"item_count": len(items), "active_count": sum(1 for item in navigation if item.get("active"))},
        children=items,
    )


def _status_bar_tree(plan: Mapping[str, Any]) -> dict[str, object]:
    status = _mapping(plan.get("status_bar"))
    return build_leaf_node(
        "status-bar",
        "StatusBar",
        role="status",
        props={"text": status.get("text"), "privacy": status.get("privacy")},
    )


def build_shell_render_tree(visible_desktop_plan: Mapping[str, Any]) -> dict[str, object]:
    """Build a renderer-neutral tree from the Qt visible desktop plan."""

    page_plan = _mapping(visible_desktop_plan.get("page"))
    page_tree = _page_tree(page_plan)
    page_root = _mapping(page_tree.get("root"))
    navigation = _navigation_tree(visible_desktop_plan)
    status = _status_bar_tree(visible_desktop_plan)
    window = _mapping(visible_desktop_plan.get("window"))
    root = build_render_node(
        "media-manager-shell",
        "ShellFrame",
        role="application_shell",
        props={
            "schema_version": SHELL_RENDER_TREE_SCHEMA_VERSION,
            "title": window.get("title") or "Media Manager",
            "active_page_id": visible_desktop_plan.get("active_page_id"),
            "requires_pyside6": False,
            "opens_window": False,
        },
        children=[navigation, dict(page_root), status],
    )
    summary = summarize_render_tree(root)
    return {
        "schema_version": SHELL_RENDER_TREE_SCHEMA_VERSION,
        "kind": "qt_shell_render_tree",
        "active_page_id": visible_desktop_plan.get("active_page_id"),
        "root": root,
        "page_tree": dict(page_tree),
        "summary": {
            **summary,
            "navigation_count": len(_list(visible_desktop_plan.get("navigation"))),
            "active_page_id": visible_desktop_plan.get("active_page_id"),
        },
    }


def summarize_shell_render_tree(tree_payload: Mapping[str, Any]) -> dict[str, object]:
    summary = _mapping(tree_payload.get("summary"))
    return {
        "schema_version": SHELL_RENDER_TREE_SCHEMA_VERSION,
        "active_page_id": tree_payload.get("active_page_id"),
        "node_count": summary.get("node_count", 0),
        "navigation_count": summary.get("navigation_count", 0),
        "sensitive_node_count": summary.get("sensitive_node_count", 0),
        "executable_node_count": summary.get("executable_node_count", 0),
    }


__all__ = ["SHELL_RENDER_TREE_SCHEMA_VERSION", "build_shell_render_tree", "summarize_shell_render_tree"]
