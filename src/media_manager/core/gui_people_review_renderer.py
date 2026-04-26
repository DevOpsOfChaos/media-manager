from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .gui_widget_specs import build_face_card_spec, build_widget_spec, summarize_widget_tree

PEOPLE_REVIEW_RENDERER_SCHEMA_VERSION = "1.0"


def _list(value: object) -> list[Any]:
    return value if isinstance(value, list) else []


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _asset_by_face_id(page_model: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    result: dict[str, Mapping[str, Any]] = {}
    for item in _list(page_model.get("asset_refs")):
        if isinstance(item, Mapping) and item.get("face_id"):
            result[str(item["face_id"])] = item
    return result


def build_people_review_render_spec(page_model: Mapping[str, Any], *, selected_group_id: str | None = None) -> dict[str, object]:
    groups = [item for item in _list(page_model.get("groups")) if isinstance(item, Mapping)]
    selected = selected_group_id or str(page_model.get("selected_group_id") or "") or (str(groups[0].get("group_id")) if groups else "")
    assets = _asset_by_face_id(page_model)

    group_widgets = []
    for group in groups:
        group_id = str(group.get("group_id") or "")
        group_widgets.append(
            build_widget_spec(
                f"group-{group_id or len(group_widgets)+1}",
                "card",
                title=str(group.get("display_label") or group_id or "Unknown person"),
                props={
                    "group_id": group_id,
                    "status": group.get("status"),
                    "selected": group_id == selected,
                    "face_count": group.get("face_count", 0),
                    "included_faces": group.get("included_faces", 0),
                    "excluded_faces": group.get("excluded_faces", 0),
                },
            )
        )

    face_widgets = []
    selected_group = next((item for item in groups if str(item.get("group_id") or "") == selected), None)
    if selected_group is not None:
        for face in _list(selected_group.get("faces")):
            if not isinstance(face, Mapping):
                continue
            face_id = str(face.get("face_id") or "")
            payload = dict(face)
            if face_id in assets:
                payload["asset_ref"] = dict(assets[face_id])
            face_widgets.append(build_face_card_spec(payload, selected=False))

    root = build_widget_spec(
        "people-review-root",
        "section",
        title=str(page_model.get("title") or "People review"),
        slots={
            "groups": build_widget_spec("people-review-groups", "list", children=group_widgets),
            "detail": build_widget_spec("people-review-detail", "panel", children=face_widgets),
            "empty_state": build_widget_spec("people-review-empty", "empty_state", props=dict(_mapping(page_model.get("empty_state")))),
        },
    )
    return {
        "schema_version": PEOPLE_REVIEW_RENDERER_SCHEMA_VERSION,
        "kind": "people_review_render_spec",
        "page_id": page_model.get("page_id", "people-review"),
        "selected_group_id": selected or None,
        "root": root,
        "summary": {
            **summarize_widget_tree(root),
            "group_count": len(groups),
            "selected_face_widget_count": len(face_widgets),
        },
    }


__all__ = ["PEOPLE_REVIEW_RENDERER_SCHEMA_VERSION", "build_people_review_render_spec"]
