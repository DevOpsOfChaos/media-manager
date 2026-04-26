from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

SELECTION_SCHEMA_VERSION = "1.0"


def _as_text(value: object) -> str:
    return value if isinstance(value, str) else ""


def _dedupe(values: Iterable[object]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        text = _as_text(value).strip()
        if text and text not in seen:
            seen.add(text)
            result.append(text)
    return result


def build_selection_state(
    *,
    active_page_id: str = "dashboard",
    selected_group_id: str | None = None,
    selected_face_id: str | None = None,
    selected_run_id: str | None = None,
    selected_profile_id: str | None = None,
    selected_face_ids: Iterable[object] = (),
) -> dict[str, object]:
    face_ids = _dedupe(selected_face_ids)
    if selected_face_id and selected_face_id not in face_ids:
        face_ids = _dedupe([*face_ids, selected_face_id])
    return {
        "schema_version": SELECTION_SCHEMA_VERSION,
        "kind": "gui_selection_state",
        "active_page_id": _as_text(active_page_id) or "dashboard",
        "selected_group_id": selected_group_id or None,
        "selected_face_id": selected_face_id or None,
        "selected_face_ids": face_ids,
        "selected_face_count": len(face_ids),
        "selected_run_id": selected_run_id or None,
        "selected_profile_id": selected_profile_id or None,
        "has_people_selection": bool(selected_group_id or face_ids),
        "has_run_selection": bool(selected_run_id),
        "has_profile_selection": bool(selected_profile_id),
    }


def select_people_group(selection: Mapping[str, Any], group_id: str, *, clear_faces: bool = True) -> dict[str, object]:
    return build_selection_state(
        active_page_id=str(selection.get("active_page_id") or "people-review"),
        selected_group_id=group_id,
        selected_face_id=None if clear_faces else selection.get("selected_face_id"),
        selected_face_ids=() if clear_faces else selection.get("selected_face_ids", ()),
        selected_run_id=selection.get("selected_run_id"),
        selected_profile_id=selection.get("selected_profile_id"),
    )


def toggle_face_selection(selection: Mapping[str, Any], face_id: str, *, multi: bool = True) -> dict[str, object]:
    normalized = _as_text(face_id).strip()
    current = _dedupe(selection.get("selected_face_ids", ()))
    if not normalized:
        return build_selection_state(
            active_page_id=str(selection.get("active_page_id") or "people-review"),
            selected_group_id=selection.get("selected_group_id"),
            selected_face_ids=current,
        )
    if not multi:
        next_faces = [] if current == [normalized] else [normalized]
    elif normalized in current:
        next_faces = [item for item in current if item != normalized]
    else:
        next_faces = [*current, normalized]
    return build_selection_state(
        active_page_id=str(selection.get("active_page_id") or "people-review"),
        selected_group_id=selection.get("selected_group_id"),
        selected_face_id=next_faces[-1] if next_faces else None,
        selected_face_ids=next_faces,
        selected_run_id=selection.get("selected_run_id"),
        selected_profile_id=selection.get("selected_profile_id"),
    )


def clear_selection(selection: Mapping[str, Any], *, keep_page: bool = True) -> dict[str, object]:
    return build_selection_state(active_page_id=str(selection.get("active_page_id") or "dashboard") if keep_page else "dashboard")


__all__ = [
    "SELECTION_SCHEMA_VERSION",
    "build_selection_state",
    "clear_selection",
    "select_people_group",
    "toggle_face_selection",
]
