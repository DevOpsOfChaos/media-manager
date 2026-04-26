from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .gui_dialog_models import build_apply_confirmation_dialog, build_people_privacy_dialog
from .gui_panel_state import normalize_panel_state
from .gui_people_review_actions import build_people_face_actions, build_people_group_actions
from .gui_people_review_timeline import build_people_review_timeline

INTERACTION_MODEL_SCHEMA_VERSION = "1.0"


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _as_text(value: Any) -> str:
    return value if isinstance(value, str) else ""


def _selected_group(page_model: Mapping[str, Any], selected_group_id: str | None) -> Mapping[str, Any]:
    groups = [item for item in _as_list(page_model.get("groups")) if isinstance(item, Mapping)]
    wanted = selected_group_id or _as_text(page_model.get("selected_group_id"))
    if wanted:
        match = next((item for item in groups if _as_text(item.get("group_id")) == wanted), None)
        if isinstance(match, Mapping):
            return match
    return groups[0] if groups else {}


def build_people_review_interaction_model(
    page_model: Mapping[str, Any],
    *,
    selected_group_id: str | None = None,
    selected_face_id: str | None = None,
    panel_state: Mapping[str, Any] | None = None,
    audit_preview: Mapping[str, Any] | None = None,
    language: str = "en",
) -> dict[str, object]:
    group = _selected_group(page_model, selected_group_id)
    detail = _as_mapping(page_model.get("detail"))
    faces = [item for item in _as_list(detail.get("faces")) if isinstance(item, Mapping)]
    wanted_face_id = selected_face_id or (faces[0].get("face_id") if faces else None)
    face = next((item for item in faces if _as_text(item.get("face_id")) == str(wanted_face_id)), faces[0] if faces else {})
    overview = _as_mapping(page_model.get("overview"))

    group_actions = build_people_group_actions(group)
    face_actions = build_people_face_actions(face)
    timeline = build_people_review_timeline(
        bundle_summary={"ready_for_gui": page_model.get("manifest_status") is not None or bool(page_model.get("bundle_ref"))},
        workspace_overview=overview,
        audit_preview=audit_preview,
    )
    ready_count = int(overview.get("ready_group_count", 0)) if isinstance(overview.get("ready_group_count"), int) else 0
    dialogs = [build_people_privacy_dialog(language=language)]
    if ready_count:
        dialogs.append(build_apply_confirmation_dialog(action_label="Apply people review", affected_count=ready_count, risk_level="high"))

    return {
        "schema_version": INTERACTION_MODEL_SCHEMA_VERSION,
        "kind": "people_review_interaction_model",
        "page_id": "people-review",
        "selected_group_id": group.get("group_id"),
        "selected_face_id": face.get("face_id") if isinstance(face, Mapping) else None,
        "panel_state": normalize_panel_state(panel_state),
        "timeline": timeline,
        "group_actions": group_actions,
        "face_actions": face_actions,
        "dialogs": dialogs,
        "ready_group_count": ready_count,
        "can_apply": any(action.get("id") == "apply_ready_groups" and action.get("enabled") for action in group_actions.get("actions", [])),
    }


__all__ = ["INTERACTION_MODEL_SCHEMA_VERSION", "build_people_review_interaction_model"]
