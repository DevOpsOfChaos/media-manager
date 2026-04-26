from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .gui_responsive_layout import build_responsive_grid

PEOPLE_REVIEW_CARD_LAYOUT_SCHEMA_VERSION = "1.0"


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def build_people_group_strip(page_model: Mapping[str, Any], *, viewport: Mapping[str, Any] | None = None) -> dict[str, object]:
    groups = [dict(item) for item in _list(page_model.get("groups")) if isinstance(item, Mapping)]
    cards = [
        {
            "id": group.get("group_id") or f"group-{index + 1}",
            "type": "group_card",
            "title": group.get("display_label") or group.get("group_id") or "Unknown person",
            "status": group.get("status"),
            "face_count": group.get("face_count", _mapping(group.get("counts")).get("face_count", 0)),
            "selected": group.get("group_id") == page_model.get("selected_group_id"),
        }
        for index, group in enumerate(groups)
    ]
    return {
        "schema_version": PEOPLE_REVIEW_CARD_LAYOUT_SCHEMA_VERSION,
        "kind": "people_group_strip",
        "group_count": len(cards),
        "grid": build_responsive_grid(cards, viewport=viewport, item_kind="people_group", max_columns=4),
    }


def build_people_face_card_layout(page_model: Mapping[str, Any], *, viewport: Mapping[str, Any] | None = None) -> dict[str, object]:
    refs = [dict(item) for item in _list(page_model.get("asset_refs")) if isinstance(item, Mapping)]
    cards = [
        {
            "id": ref.get("face_id") or ref.get("id") or f"face-{index + 1}",
            "type": "face_card",
            "asset_ref": ref,
            "status": ref.get("status") or "unknown",
            "sensitive": True,
        }
        for index, ref in enumerate(refs)
    ]
    return {
        "schema_version": PEOPLE_REVIEW_CARD_LAYOUT_SCHEMA_VERSION,
        "kind": "people_face_card_layout",
        "face_count": len(cards),
        "grid": build_responsive_grid(cards, viewport=viewport, item_kind="people_face", max_columns=6),
        "privacy_notice": "Face cards can reveal sensitive biometric context and should stay local/private.",
    }


__all__ = ["PEOPLE_REVIEW_CARD_LAYOUT_SCHEMA_VERSION", "build_people_face_card_layout", "build_people_group_strip"]
