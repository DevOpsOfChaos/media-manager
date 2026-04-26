from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

QUEUE_SCHEMA_VERSION = "1.0"
STATUS_ORDER = {
    "needs_name": 0,
    "needs_review": 1,
    "named_not_applied": 2,
    "ready_to_apply": 3,
    "all_faces_rejected": 4,
}


def _text(value: object) -> str:
    return str(value) if value is not None else ""


def build_people_review_queue(groups: Iterable[Mapping[str, Any]], *, query: str = "", status_filter: str = "all", limit: int = 200) -> dict[str, object]:
    normalized_query = query.strip().casefold()
    normalized_status = status_filter.strip().casefold() or "all"
    rows: list[dict[str, object]] = []
    for group in groups:
        item = dict(group)
        label = _text(item.get("display_label") or item.get("group_id"))
        status = _text(item.get("status") or "needs_review")
        text = f"{label} {status} {item.get('group_id', '')}".casefold()
        if normalized_query and normalized_query not in text:
            continue
        if normalized_status != "all" and normalized_status != status.casefold():
            continue
        counts = item.get("counts") if isinstance(item.get("counts"), Mapping) else {}
        rows.append(
            {
                "group_id": item.get("group_id"),
                "display_label": label,
                "status": status,
                "primary_face_id": item.get("primary_face_id"),
                "face_count": item.get("face_count", counts.get("face_count", 0)),
                "included_faces": item.get("included_faces", counts.get("included_faces", 0)),
                "excluded_faces": item.get("excluded_faces", counts.get("excluded_faces", 0)),
                "sort_rank": STATUS_ORDER.get(status, 99),
            }
        )
    rows.sort(key=lambda row: (row["sort_rank"], -int(row.get("face_count") or 0), _text(row.get("display_label")).casefold()))
    limited = rows[: max(0, limit)]
    total_group_count = len(rows)
    returned_group_count = len(limited)
    return {
        "schema_version": QUEUE_SCHEMA_VERSION,
        "kind": "people_review_queue",
        "query": query,
        "status_filter": status_filter,
        # Backward-compatible alias expected by older page-model tests and GUI callers.
        # This represents the filtered total before applying the display limit.
        "group_count": total_group_count,
        "total_group_count": total_group_count,
        "returned_group_count": returned_group_count,
        "truncated": total_group_count > returned_group_count,
        "groups": limited,
    }


__all__ = ["QUEUE_SCHEMA_VERSION", "build_people_review_queue"]
