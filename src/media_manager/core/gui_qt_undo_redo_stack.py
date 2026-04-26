from __future__ import annotations

from collections.abc import Mapping
from typing import Any

UNDO_REDO_SCHEMA_VERSION = "1.0"


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def build_undo_redo_stack(*, undo: list[Mapping[str, Any]] | None = None, redo: list[Mapping[str, Any]] | None = None, limit: int = 100) -> dict[str, Any]:
    max_items = max(1, int(limit))
    undo_items = [dict(item) for item in (undo or [])][-max_items:]
    redo_items = [dict(item) for item in (redo or [])][-max_items:]
    return {
        "schema_version": UNDO_REDO_SCHEMA_VERSION,
        "undo": undo_items,
        "redo": redo_items,
        "limit": max_items,
        "can_undo": bool(undo_items),
        "can_redo": bool(redo_items),
        "undo_count": len(undo_items),
        "redo_count": len(redo_items),
    }


def push_undo(stack: Mapping[str, Any], change: Mapping[str, Any]) -> dict[str, Any]:
    undo = [*(_as_list(stack.get("undo"))), dict(change)]
    return build_undo_redo_stack(undo=undo, redo=[], limit=int(stack.get("limit", 100)))


def undo_once(stack: Mapping[str, Any]) -> dict[str, Any]:
    undo = [dict(item) for item in _as_list(stack.get("undo"))]
    redo = [dict(item) for item in _as_list(stack.get("redo"))]
    if not undo:
        return build_undo_redo_stack(undo=undo, redo=redo, limit=int(stack.get("limit", 100)))
    moved = undo.pop()
    moved["undo_applied"] = True
    redo.append(moved)
    return build_undo_redo_stack(undo=undo, redo=redo, limit=int(stack.get("limit", 100)))


def redo_once(stack: Mapping[str, Any]) -> dict[str, Any]:
    undo = [dict(item) for item in _as_list(stack.get("undo"))]
    redo = [dict(item) for item in _as_list(stack.get("redo"))]
    if not redo:
        return build_undo_redo_stack(undo=undo, redo=redo, limit=int(stack.get("limit", 100)))
    moved = redo.pop()
    moved["redo_applied"] = True
    undo.append(moved)
    return build_undo_redo_stack(undo=undo, redo=redo, limit=int(stack.get("limit", 100)))


__all__ = ["UNDO_REDO_SCHEMA_VERSION", "build_undo_redo_stack", "push_undo", "redo_once", "undo_once"]
