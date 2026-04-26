from __future__ import annotations

from collections.abc import Mapping
from typing import Any

PAGE_SLOTS_SCHEMA_VERSION = "1.0"


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def build_page_slots(page_model: Mapping[str, Any]) -> dict[str, object]:
    kind = str(page_model.get("kind") or "unknown")
    slots: list[dict[str, object]] = []
    slots.append({"id": "header", "kind": "header", "required": True, "available": bool(page_model.get("title"))})
    if kind == "dashboard_page":
        slots.extend([
            {"id": "hero", "kind": "hero", "required": True, "available": "hero" in page_model},
            {"id": "cards", "kind": "card_grid", "required": True, "available": bool(_as_list(page_model.get("cards")))},
            {"id": "activity", "kind": "activity", "required": False, "available": bool(page_model.get("activity"))},
        ])
    elif kind == "people_review_page":
        slots.extend([
            {"id": "queue", "kind": "master_list", "required": True, "available": "queue" in page_model},
            {"id": "detail", "kind": "detail_panel", "required": True, "available": "detail" in page_model},
            {"id": "faces", "kind": "face_strip", "required": False, "available": bool(_as_list(_as_mapping(page_model.get("detail")).get("faces")))},
        ])
    elif kind in {"table_page", "profiles_page"}:
        slots.append({"id": "table", "kind": "table", "required": True, "available": bool(_as_list(page_model.get("rows"))) or bool(page_model.get("empty_state"))})
    else:
        slots.append({"id": "empty", "kind": "empty_state", "required": False, "available": bool(page_model.get("empty_state"))})
    missing_required = [slot["id"] for slot in slots if slot.get("required") and not slot.get("available")]
    return {
        "schema_version": PAGE_SLOTS_SCHEMA_VERSION,
        "kind": "page_slots",
        "page_id": page_model.get("page_id"),
        "page_kind": kind,
        "slots": slots,
        "slot_count": len(slots),
        "missing_required_slots": missing_required,
        "ready": not missing_required,
    }


__all__ = ["PAGE_SLOTS_SCHEMA_VERSION", "build_page_slots"]
