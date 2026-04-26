from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .gui_file_refs import build_local_file_ref

PEOPLE_REVIEW_GUI_SCHEMA_VERSION = "1.0"


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def build_people_review_card_grid(page_model: Mapping[str, Any], *, face_limit: int = 200) -> dict[str, object]:
    groups = [item for item in _as_list(page_model.get("groups")) if isinstance(item, Mapping)]
    assets = [item for item in _as_list(page_model.get("asset_refs")) if isinstance(item, Mapping)]
    assets_by_face_id = {str(item.get("face_id")): item for item in assets if item.get("face_id")}
    cards: list[dict[str, object]] = []
    for group in groups:
        primary_face_id = str(group.get("primary_face_id") or "")
        asset = assets_by_face_id.get(primary_face_id, {})
        cards.append(
            {
                "group_id": group.get("group_id"),
                "display_label": group.get("display_label"),
                "status": group.get("status"),
                "face_count": group.get("face_count", 0),
                "included_faces": group.get("included_faces", 0),
                "excluded_faces": group.get("excluded_faces", 0),
                "primary_face_id": primary_face_id or None,
                "thumbnail_ref": asset.get("file_ref") or build_local_file_ref(None, role="face_crop"),
                "actions": ["open_group", "accept_group", "reject_wrong_faces"],
            }
        )
        if len(cards) >= max(0, face_limit):
            break
    return {
        "schema_version": PEOPLE_REVIEW_GUI_SCHEMA_VERSION,
        "kind": "people_review_card_grid",
        "group_count": len(groups),
        "card_count": len(cards),
        "cards": cards,
        "empty_state": page_model.get("empty_state") if not cards else None,
    }


def build_people_review_detail_model(page_model: Mapping[str, Any], group_id: str | None = None) -> dict[str, object]:
    groups = [item for item in _as_list(page_model.get("groups")) if isinstance(item, Mapping)]
    selected = None
    if group_id:
        selected = next((item for item in groups if str(item.get("group_id")) == str(group_id)), None)
    if selected is None and groups:
        selected = groups[0]
    return {
        "schema_version": PEOPLE_REVIEW_GUI_SCHEMA_VERSION,
        "kind": "people_review_detail",
        "selected_group_id": selected.get("group_id") if isinstance(selected, Mapping) else None,
        "selected_group": dict(selected) if isinstance(selected, Mapping) else None,
        "review_controls": ["selected_name", "apply_group", "faces.include", "faces.note", "split_group", "merge_group"],
    }


__all__ = ["PEOPLE_REVIEW_GUI_SCHEMA_VERSION", "build_people_review_card_grid", "build_people_review_detail_model"]
