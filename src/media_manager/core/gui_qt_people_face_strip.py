from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

FACE_STRIP_SCHEMA_VERSION = "1.0"


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def build_face_strip_item(face: Mapping[str, Any], *, selected_face_id: str | None = None) -> dict[str, object]:
    face_id = str(face.get("face_id") or face.get("id") or "")
    path = face.get("path") or face.get("image_path") or face.get("asset_path")
    include = face.get("include")
    status = "included" if include is True else "excluded" if include is False else str(face.get("status") or "pending")
    return {
        "schema_version": FACE_STRIP_SCHEMA_VERSION,
        "kind": "face_strip_item",
        "face_id": face_id,
        "path": str(path) if path is not None else None,
        "status": status,
        "selected": bool(selected_face_id and face_id == selected_face_id),
        "sensitive": True,
        "thumbnail_role": "face_crop",
    }


def build_people_face_strip(faces: Iterable[Mapping[str, Any]] | None = None, *, selected_face_id: str | None = None, limit: int = 48) -> dict[str, object]:
    items = [build_face_strip_item(_as_mapping(face), selected_face_id=selected_face_id) for face in list(faces or [])[: max(0, limit)]]
    return {
        "schema_version": FACE_STRIP_SCHEMA_VERSION,
        "kind": "people_face_strip",
        "items": items,
        "face_count": len(items),
        "selected_face_id": selected_face_id,
        "sensitive": True,
        "truncated": len(list(faces or [])) > len(items),
    }


def build_people_face_strip_from_page(page_model: Mapping[str, Any], *, selected_face_id: str | None = None, limit: int = 48) -> dict[str, object]:
    detail_faces = _as_list(_as_mapping(page_model.get("detail")).get("faces"))
    if not detail_faces:
        detail_faces = _as_list(page_model.get("asset_refs"))
    return build_people_face_strip([_as_mapping(face) for face in detail_faces if isinstance(face, Mapping)], selected_face_id=selected_face_id, limit=limit)


__all__ = ["FACE_STRIP_SCHEMA_VERSION", "build_people_face_strip", "build_people_face_strip_from_page", "build_face_strip_item"]
