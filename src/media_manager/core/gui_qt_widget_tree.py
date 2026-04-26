from __future__ import annotations

from collections.abc import Mapping
from typing import Any

WIDGET_TREE_SCHEMA_VERSION = "1.0"


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _text(value: Any, default: str = "") -> str:
    return str(value) if value is not None else default


def _widget(widget_id: str, widget_type: str, *, role: str = "", props: Mapping[str, Any] | None = None, children: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    return {
        "id": widget_id,
        "type": widget_type,
        "role": role or widget_type,
        "props": dict(props or {}),
        "children": list(children or []),
    }


def build_widget_tree_from_page_plan(page_plan: Mapping[str, Any]) -> dict[str, Any]:
    """Build a renderer-neutral widget tree from a Qt page plan.

    The tree is intentionally declarative. It does not import Qt and does not
    create widgets. The future Qt runtime can use it as the single source of
    truth for constructing visual components.
    """

    page_id = _text(page_plan.get("page_id"), "page")
    sections = [item for item in _as_list(page_plan.get("sections")) if isinstance(item, Mapping)]
    if not sections and isinstance(page_plan.get("widgets"), list):
        sections = [page_plan]

    children: list[dict[str, Any]] = []
    for section_index, section in enumerate(sections):
        section_id = _text(section.get("id"), f"section-{section_index + 1}")
        raw_widgets = [item for item in _as_list(section.get("widgets")) if isinstance(item, Mapping)]
        widgets = []
        for widget_index, raw_widget in enumerate(raw_widgets):
            widget_type = _text(raw_widget.get("type"), "unknown")
            widgets.append(
                _widget(
                    f"{section_id}-widget-{widget_index + 1}",
                    widget_type,
                    role=_text(raw_widget.get("role"), widget_type),
                    props={key: value for key, value in raw_widget.items() if key not in {"children"}},
                    children=[
                        _widget(f"{section_id}-widget-{widget_index + 1}-child-{child_index + 1}", _text(child.get("type"), "unknown"), props=child)
                        for child_index, child in enumerate(_as_list(raw_widget.get("children")))
                        if isinstance(child, Mapping)
                    ],
                )
            )
        children.append(
            _widget(
                f"{page_id}-{section_id}",
                "section",
                role=_text(section.get("role"), "page_section"),
                props={"title": section.get("title"), "layout": section.get("layout")},
                children=widgets,
            )
        )

    tree = _widget(
        f"{page_id}-root",
        "page",
        role="page_root",
        props={"page_id": page_id, "title": page_plan.get("title"), "layout": page_plan.get("layout")},
        children=children,
    )
    return {
        "schema_version": WIDGET_TREE_SCHEMA_VERSION,
        "kind": "qt_widget_tree",
        "page_id": page_id,
        "root": tree,
        "summary": summarize_widget_tree(tree),
    }


def _walk_widgets(widget: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    result = [widget]
    for child in _as_list(widget.get("children")):
        if isinstance(child, Mapping):
            result.extend(_walk_widgets(child))
    return result


def summarize_widget_tree(root: Mapping[str, Any]) -> dict[str, Any]:
    widgets = _walk_widgets(root)
    type_summary: dict[str, int] = {}
    for widget in widgets:
        widget_type = _text(widget.get("type"), "unknown")
        type_summary[widget_type] = type_summary.get(widget_type, 0) + 1
    return {
        "widget_count": len(widgets),
        "type_summary": dict(sorted(type_summary.items())),
        "section_count": type_summary.get("section", 0),
    }


def validate_widget_tree(tree_payload: Mapping[str, Any]) -> dict[str, Any]:
    problems: list[str] = []
    root = _as_mapping(tree_payload.get("root"))
    if not root:
        problems.append("missing_root")
    if root and root.get("type") != "page":
        problems.append("root_must_be_page")
    summary = _as_mapping(tree_payload.get("summary"))
    if int(summary.get("widget_count", 0) or 0) <= 0:
        problems.append("empty_widget_tree")
    return {"valid": not problems, "problems": problems, "problem_count": len(problems)}


__all__ = [
    "WIDGET_TREE_SCHEMA_VERSION",
    "build_widget_tree_from_page_plan",
    "summarize_widget_tree",
    "validate_widget_tree",
]
