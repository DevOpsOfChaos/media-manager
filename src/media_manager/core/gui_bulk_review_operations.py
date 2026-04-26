from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

BULK_OPERATION_SCHEMA_VERSION = "1.0"


def _dedupe(values: Iterable[object]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        text = value if isinstance(value, str) else ""
        text = text.strip()
        if text and text not in seen:
            seen.add(text)
            result.append(text)
    return result


def build_bulk_review_operation(
    operation_id: str,
    *,
    group_id: str | None = None,
    face_ids: Iterable[object] = (),
    selected_name: str | None = None,
    note: str = "",
) -> dict[str, object]:
    normalized_faces = _dedupe(face_ids)
    op = str(operation_id or "").strip() or "noop"
    requires_confirmation = op in {"apply_ready", "reject_selected", "split_selected"}
    return {
        "schema_version": BULK_OPERATION_SCHEMA_VERSION,
        "kind": "gui_bulk_review_operation",
        "operation_id": op,
        "group_id": group_id or None,
        "face_ids": normalized_faces,
        "face_count": len(normalized_faces),
        "selected_name": selected_name or None,
        "note": note,
        "requires_confirmation": requires_confirmation,
        "executes_immediately": False,
        "valid": _is_valid_operation(op, group_id=group_id, face_ids=normalized_faces, selected_name=selected_name),
    }


def _is_valid_operation(operation_id: str, *, group_id: str | None, face_ids: list[str], selected_name: str | None) -> bool:
    if operation_id in {"accept_group", "apply_ready"}:
        return bool(group_id)
    if operation_id == "rename_group":
        return bool(group_id and selected_name)
    if operation_id in {"reject_selected", "split_selected"}:
        return bool(group_id and face_ids)
    if operation_id == "noop":
        return False
    return bool(group_id or face_ids)


def operation_from_selection(action_id: str, selection: Mapping[str, Any], *, selected_name: str | None = None, note: str = "") -> dict[str, object]:
    return build_bulk_review_operation(
        action_id,
        group_id=selection.get("selected_group_id") if isinstance(selection.get("selected_group_id"), str) else None,
        face_ids=selection.get("selected_face_ids", ()) if isinstance(selection.get("selected_face_ids"), list) else (),
        selected_name=selected_name,
        note=note,
    )


def summarize_bulk_operations(operations: Iterable[Mapping[str, Any]]) -> dict[str, object]:
    items = [dict(item) for item in operations]
    return {
        "schema_version": BULK_OPERATION_SCHEMA_VERSION,
        "kind": "gui_bulk_review_operation_summary",
        "operation_count": len(items),
        "valid_count": sum(1 for item in items if item.get("valid") is True),
        "confirmation_required_count": sum(1 for item in items if item.get("requires_confirmation") is True),
        "operation_ids": [str(item.get("operation_id")) for item in items],
    }


__all__ = [
    "BULK_OPERATION_SCHEMA_VERSION",
    "build_bulk_review_operation",
    "operation_from_selection",
    "summarize_bulk_operations",
]
