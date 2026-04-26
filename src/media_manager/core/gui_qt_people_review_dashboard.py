from __future__ import annotations

from collections.abc import Mapping
from typing import Any

PEOPLE_REVIEW_DASHBOARD_SCHEMA_VERSION = "1.0"


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def build_people_review_dashboard(page_model: Mapping[str, Any], *, language: str = "en") -> dict[str, object]:
    groups = [item for item in _list(page_model.get("groups")) if isinstance(item, Mapping)]
    queue = _mapping(page_model.get("queue"))
    overview = _mapping(page_model.get("overview"))
    status_counts: dict[str, int] = {}
    for group in groups:
        status = str(group.get("status") or "unknown")
        status_counts[status] = status_counts.get(status, 0) + 1
    ready_count = status_counts.get("ready_to_apply", 0) + status_counts.get("ready", 0)
    needs_name = status_counts.get("needs_name", 0)
    needs_review = status_counts.get("needs_review", 0)
    title = "Personenprüfung" if str(language).lower().startswith("de") else "People review"
    return {
        "schema_version": PEOPLE_REVIEW_DASHBOARD_SCHEMA_VERSION,
        "kind": "qt_people_review_dashboard",
        "title": title,
        "group_count": len(groups),
        "face_count": overview.get("face_count", overview.get("faces", 0)),
        "ready_group_count": ready_count,
        "needs_name_group_count": needs_name,
        "needs_review_group_count": needs_review,
        "status_counts": dict(sorted(status_counts.items())),
        "queue_summary": {
            "query": queue.get("query", ""),
            "returned_group_count": queue.get("returned_group_count", queue.get("group_count", len(groups))),
            "truncated": bool(queue.get("truncated", False)),
        },
        "attention_count": needs_name + needs_review,
        "safe_to_apply": ready_count > 0 and needs_name == 0 and needs_review == 0,
    }


__all__ = ["PEOPLE_REVIEW_DASHBOARD_SCHEMA_VERSION", "build_people_review_dashboard"]
