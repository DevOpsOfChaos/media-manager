from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .gui_qt_render_tree import build_leaf_node, build_render_node, summarize_render_tree

PEOPLE_REVIEW_RENDER_TREE_SCHEMA_VERSION = "1.0"


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


def _component_for_child(child: Mapping[str, Any]) -> tuple[str, str, bool]:
    kind = str(child.get("kind") or "item")
    if kind == "people_group_button":
        return "PeopleGroupButton", "people_group", False
    if kind == "people_face_card":
        return "FaceCard", "people_face", True
    if kind == "text":
        return "Text", str(child.get("role") or "text"), False
    return "PeopleReviewItem", kind, bool(child.get("sensitive"))


def _section_component(section: Mapping[str, Any]) -> str:
    variant = str(section.get("variant") or "")
    section_id = str(section.get("section_id") or "")
    if variant == "master_list" or section_id.endswith("groups"):
        return "PeopleGroupLane"
    if variant == "detail_grid" or section_id.endswith("detail"):
        return "FaceGallery"
    if variant == "empty_state":
        return "EmptyStateSection"
    return "PeopleReviewSection"


def _child_node(section_id: str, child: Mapping[str, Any], index: int) -> dict[str, object]:
    component, role, sensitive = _component_for_child(child)
    child_id = child.get("face_id") or child.get("group_id") or child.get("id") or f"item-{index + 1}"
    return build_leaf_node(
        f"{section_id}-{child_id}",
        component,
        role=role,
        props={
            key: value
            for key, value in dict(child).items()
            if key not in {"asset_ref"} or isinstance(value, Mapping)
        },
        sensitive=sensitive,
    )


def _section_node(section: Mapping[str, Any], index: int) -> dict[str, object]:
    section_id = _text(section.get("section_id") or section.get("id"), f"people-review-section-{index + 1}")
    children = [
        _child_node(section_id, child, child_index)
        for child_index, child in enumerate(_list(section.get("children")))
        if isinstance(child, Mapping)
    ]
    return build_render_node(
        section_id,
        _section_component(section),
        role="people_review_section",
        props={
            "section_id": section_id,
            "title": section.get("title"),
            "subtitle": section.get("subtitle"),
            "variant": section.get("variant"),
            "child_count": len(children),
        },
        children=children,
        sensitive=any(bool(child.get("sensitive")) for child in children),
    )


def build_people_review_render_tree(page_plan: Mapping[str, Any]) -> dict[str, object]:
    """Convert a People Review visible page plan into a headless render tree.

    Face cards are marked sensitive because they may reference local face-crop
    assets. The tree remains local data only and never executes review/apply
    actions immediately.
    """

    body = _body_from_page_plan(page_plan)
    page_id = _text(page_plan.get("page_id") or body.get("page_id"), "people-review")
    sections = [section for section in _list(body.get("sections")) if isinstance(section, Mapping)]
    section_nodes = [_section_node(section, index) for index, section in enumerate(sections)]
    privacy_notice = body.get("privacy_notice") or "Face crops are sensitive local biometric data."
    root = build_render_node(
        f"{page_id}-root",
        "PeopleReviewPage",
        role="page",
        props={
            "schema_version": PEOPLE_REVIEW_RENDER_TREE_SCHEMA_VERSION,
            "page_id": page_id,
            "layout": body.get("layout") or "master_detail_faces",
            "group_count": body.get("group_count", 0),
            "face_count": body.get("face_count", 0),
            "selected_group_id": body.get("selected_group_id"),
            "privacy_notice": privacy_notice,
        },
        children=section_nodes,
        sensitive=any(bool(child.get("sensitive")) for child in section_nodes),
    )
    return {
        "schema_version": PEOPLE_REVIEW_RENDER_TREE_SCHEMA_VERSION,
        "kind": "qt_people_review_render_tree",
        "page_id": page_id,
        "root": root,
        "summary": summarize_render_tree(root),
        "privacy_notice": privacy_notice,
    }


__all__ = ["PEOPLE_REVIEW_RENDER_TREE_SCHEMA_VERSION", "build_people_review_render_tree"]
