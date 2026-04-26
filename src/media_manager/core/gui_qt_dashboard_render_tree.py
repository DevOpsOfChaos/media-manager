from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .gui_qt_render_tree import build_leaf_node, build_render_node, summarize_render_tree

DASHBOARD_RENDER_TREE_SCHEMA_VERSION = "1.0"


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: object) -> list[Any]:
    return value if isinstance(value, list) else []


def _text(value: object, fallback: str = "") -> str:
    text = str(value).strip() if value is not None else ""
    return text or fallback


def _body_from_page_plan(page_plan: Mapping[str, Any]) -> Mapping[str, Any]:
    body = _mapping(page_plan.get("body"))
    return body if body else page_plan


def _section_id(section: Mapping[str, Any], index: int) -> str:
    return _text(section.get("section_id") or section.get("id") or section.get("kind"), f"dashboard-section-{index + 1}")


def _component_for_section(section: Mapping[str, Any]) -> str:
    variant = _text(section.get("variant") or section.get("kind"), "section")
    if variant == "hero":
        return "HeroSection"
    if variant in {"activity", "activity_section"}:
        return "ActivitySection"
    if variant == "card_grid_section":
        return "CardGridSection"
    if variant == "empty_state":
        return "EmptyStateSection"
    return "Section"


def _metric_nodes(section_id: str, children: list[Any]) -> list[dict[str, object]]:
    nodes: list[dict[str, object]] = []
    for index, item in enumerate(children):
        if not isinstance(item, Mapping):
            continue
        if item.get("kind") == "metric_strip":
            metrics = _mapping(item.get("metrics"))
            metric_children = [
                build_leaf_node(
                    f"{section_id}-metric-{key}",
                    "Metric",
                    role="dashboard_metric",
                    props={"name": str(key), "value": value},
                )
                for key, value in sorted(metrics.items())
            ]
            nodes.append(
                build_render_node(
                    f"{section_id}-metric-strip-{index + 1}",
                    "MetricStrip",
                    role="dashboard_metric_strip",
                    props={"metric_count": len(metric_children)},
                    children=metric_children,
                )
            )
        else:
            nodes.append(
                build_leaf_node(
                    f"{section_id}-item-{index + 1}",
                    "DashboardItem",
                    role=str(item.get("kind") or "dashboard_item"),
                    props=dict(item),
                )
            )
    return nodes


def _card_grid_nodes(section_id: str, section: Mapping[str, Any]) -> list[dict[str, object]]:
    grid = _mapping(section.get("grid"))
    cards = [item for item in _list(grid.get("cards")) if isinstance(item, Mapping)]
    card_nodes = [
        build_leaf_node(
            f"{section_id}-{card.get('card_id') or index + 1}",
            "Card",
            role="dashboard_card",
            props={
                "card_id": card.get("card_id"),
                "title": card.get("title"),
                "subtitle": card.get("subtitle"),
                "metric_count": card.get("metric_count", 0),
                "action_count": len(_list(card.get("actions"))),
            },
        )
        for index, card in enumerate(cards)
    ]
    if not card_nodes:
        return []
    return [
        build_render_node(
            f"{section_id}-card-grid",
            "CardGrid",
            role="dashboard_card_grid",
            props={
                "columns": grid.get("columns"),
                "card_count": grid.get("card_count", len(card_nodes)),
                "visible_card_count": grid.get("visible_card_count", len(card_nodes)),
                "truncated": bool(grid.get("truncated")),
            },
            children=card_nodes,
        )
    ]


def _section_node(section: Mapping[str, Any], index: int) -> dict[str, object]:
    section_id = _section_id(section, index)
    children = _metric_nodes(section_id, _list(section.get("children")))
    children.extend(_card_grid_nodes(section_id, section))
    return build_render_node(
        section_id,
        _component_for_section(section),
        role="dashboard_section",
        props={
            "section_id": section_id,
            "title": section.get("title"),
            "subtitle": section.get("subtitle"),
            "variant": section.get("variant") or section.get("kind"),
            "collapsible": bool(section.get("collapsible")),
            "collapsed": bool(section.get("collapsed")),
        },
        children=children,
    )


def build_dashboard_render_tree(page_plan: Mapping[str, Any]) -> dict[str, object]:
    """Convert a dashboard visible page plan into a declarative render tree."""

    body = _body_from_page_plan(page_plan)
    page_id = _text(page_plan.get("page_id") or body.get("page_id"), "dashboard")
    sections = [section for section in _list(body.get("sections")) if isinstance(section, Mapping)]
    section_nodes = [_section_node(section, index) for index, section in enumerate(sections)]
    root = build_render_node(
        f"{page_id}-dashboard-root",
        "DashboardPage",
        role="page",
        props={
            "schema_version": DASHBOARD_RENDER_TREE_SCHEMA_VERSION,
            "page_id": page_id,
            "title": page_plan.get("title") or body.get("title") or "Dashboard",
            "layout": body.get("layout") or page_plan.get("layout"),
            "section_count": len(section_nodes),
        },
        children=section_nodes,
    )
    return {
        "schema_version": DASHBOARD_RENDER_TREE_SCHEMA_VERSION,
        "kind": "qt_dashboard_render_tree",
        "page_id": page_id,
        "root": root,
        "summary": summarize_render_tree(root),
    }


__all__ = ["DASHBOARD_RENDER_TREE_SCHEMA_VERSION", "build_dashboard_render_tree"]
