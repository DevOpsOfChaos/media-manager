from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .gui_qt_section_plan import build_empty_state_section, build_qt_section_plan

PEOPLE_REVIEW_VISIBLE_PLAN_SCHEMA_VERSION = "1.0"


_STATUS_PRIORITY = {
    "needs_name": 0,
    "needs_review": 1,
    "ready_to_apply": 2,
    "named_not_applied": 3,
    "all_faces_rejected": 4,
}


def _as_mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _as_list(value: object) -> list[Any]:
    return value if isinstance(value, list) else []


def _group_priority(group: Mapping[str, Any]) -> tuple[int, str]:
    return (_STATUS_PRIORITY.get(str(group.get("status")), 9), str(group.get("display_label") or group.get("group_id") or "").casefold())


def _group_item(group: Mapping[str, Any], *, selected_group_id: str | None) -> dict[str, object]:
    group_id = str(group.get("group_id") or "")
    return {
        "kind": "people_group_button",
        "group_id": group_id,
        "label": str(group.get("display_label") or group_id or "Unknown person"),
        "status": str(group.get("status") or "unknown"),
        "face_count": int(group.get("face_count") or 0),
        "included_faces": int(group.get("included_faces") or 0),
        "excluded_faces": int(group.get("excluded_faces") or 0),
        "selected": bool(selected_group_id and group_id == selected_group_id),
    }


def _face_item(face: Mapping[str, Any]) -> dict[str, object]:
    asset_ref = _as_mapping(face.get("asset_ref"))
    return {
        "kind": "people_face_card",
        "face_id": str(face.get("face_id") or ""),
        "title": str(face.get("face_id") or "Face"),
        "subtitle": str(face.get("path") or asset_ref.get("path") or ""),
        "asset_ref": dict(asset_ref),
        "decision_status": str(face.get("decision_status") or face.get("status") or "pending"),
        "sensitive": True,
    }


def build_qt_people_review_visible_plan(
    page_model: Mapping[str, Any],
    *,
    selected_group_id: str | None = None,
    max_groups: int = 80,
    max_faces: int = 48,
) -> dict[str, object]:
    groups = [item for item in _as_list(page_model.get("groups")) if isinstance(item, Mapping)]
    groups.sort(key=_group_priority)
    selected = selected_group_id or str(page_model.get("selected_group_id") or "")
    if not selected and groups:
        selected = str(groups[0].get("group_id") or "")
    visible_groups = groups[: max(0, int(max_groups))]
    detail = _as_mapping(page_model.get("detail"))
    faces = [item for item in _as_list(detail.get("faces")) if isinstance(item, Mapping)]
    visible_faces = faces[: max(0, int(max_faces))]
    if not groups:
        empty = build_empty_state_section("people-review", _as_mapping(page_model.get("empty_state")))
    else:
        empty = None
    group_section = build_qt_section_plan(
        "people-review-groups",
        title="Groups",
        subtitle=str(page_model.get("query") or ""),
        variant="master_list",
        children=[_group_item(group, selected_group_id=selected) for group in visible_groups],
    )
    detail_section = build_qt_section_plan(
        "people-review-detail",
        title=str(detail.get("title") or "Selection"),
        subtitle=str(detail.get("subtitle") or ""),
        variant="detail_grid",
        children=[_face_item(face) for face in visible_faces],
    )
    return {
        "schema_version": PEOPLE_REVIEW_VISIBLE_PLAN_SCHEMA_VERSION,
        "kind": "qt_people_review_visible_plan",
        "page_id": "people-review",
        "layout": "master_detail_faces",
        "selected_group_id": selected or None,
        "group_count": len(groups),
        "visible_group_count": len(visible_groups),
        "face_count": len(faces),
        "visible_face_count": len(visible_faces),
        "groups_truncated": len(groups) > len(visible_groups),
        "faces_truncated": len(faces) > len(visible_faces),
        "sections": [section for section in (group_section, detail_section, empty) if section is not None],
        "privacy_notice": "Face crops are sensitive local biometric data.",
    }


__all__ = ["PEOPLE_REVIEW_VISIBLE_PLAN_SCHEMA_VERSION", "build_qt_people_review_visible_plan"]
