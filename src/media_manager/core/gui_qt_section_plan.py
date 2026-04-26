from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

SECTION_PLAN_SCHEMA_VERSION = "1.0"


def _text(value: object, fallback: str = "") -> str:
    text = str(value).strip() if value is not None else ""
    return text or fallback


def _list(value: object) -> list[Any]:
    return value if isinstance(value, list) else []


def build_qt_section_plan(
    section_id: str,
    *,
    title: str,
    subtitle: str = "",
    children: Iterable[Mapping[str, Any]] = (),
    variant: str = "default",
    collapsible: bool = False,
    collapsed: bool = False,
) -> dict[str, object]:
    """Build a renderer-facing section plan for the Qt shell.

    This remains a pure data contract. It does not import PySide6 and does not
    instantiate widgets, so it can be tested in headless CI.
    """

    child_list = [dict(item) for item in children]
    return {
        "schema_version": SECTION_PLAN_SCHEMA_VERSION,
        "kind": "qt_section_plan",
        "section_id": _text(section_id, "section"),
        "title": _text(title, "Section"),
        "subtitle": _text(subtitle),
        "variant": _text(variant, "default"),
        "collapsible": bool(collapsible),
        "collapsed": bool(collapsed) if collapsible else False,
        "child_count": len(child_list),
        "children": child_list,
        "qt": {
            "widget": "QFrame",
            "object_name": "Section",
            "layout": "QVBoxLayout",
        },
    }


def build_empty_state_section(page_id: str, empty_state: Mapping[str, Any] | None = None) -> dict[str, object]:
    payload = dict(empty_state or {})
    title = payload.get("title") or "Nothing to show yet"
    description = payload.get("description") or "Open or create the required artifacts to populate this view."
    return build_qt_section_plan(
        f"{page_id}-empty-state",
        title=str(title),
        subtitle=str(description),
        variant="empty_state",
        children=[
            {
                "kind": "text",
                "role": "empty_state_title",
                "text": str(title),
            },
            {
                "kind": "text",
                "role": "empty_state_description",
                "text": str(description),
            },
        ],
    )


def summarize_section_plan(plan: Mapping[str, Any]) -> dict[str, object]:
    return {
        "section_id": plan.get("section_id"),
        "title": plan.get("title"),
        "variant": plan.get("variant"),
        "child_count": len(_list(plan.get("children"))),
        "collapsed": bool(plan.get("collapsed")),
    }


__all__ = [
    "SECTION_PLAN_SCHEMA_VERSION",
    "build_empty_state_section",
    "build_qt_section_plan",
    "summarize_section_plan",
]
