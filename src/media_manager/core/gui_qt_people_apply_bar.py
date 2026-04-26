from __future__ import annotations

from collections.abc import Mapping
from typing import Any

PEOPLE_APPLY_BAR_SCHEMA_VERSION = "1.0"


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _int(value: Any) -> int:
    return value if isinstance(value, int) else 0


def build_people_apply_bar(audit_payload: Mapping[str, Any] | None = None, *, confirmation_acknowledged: bool = False) -> dict[str, object]:
    audit_payload = _mapping(audit_payload)
    summary = _mapping(audit_payload.get("summary"))
    ready_groups = _int(summary.get("ready_group_count") or summary.get("groups_ready") or audit_payload.get("ready_group_count"))
    blocked_groups = _int(summary.get("blocked_group_count") or summary.get("groups_blocked") or audit_payload.get("blocked_group_count"))
    embeddings = _int(summary.get("embedding_count") or summary.get("embeddings_to_write") or audit_payload.get("embedding_count"))
    enabled = ready_groups > 0 and blocked_groups == 0 and bool(confirmation_acknowledged)
    return {
        "schema_version": PEOPLE_APPLY_BAR_SCHEMA_VERSION,
        "kind": "qt_people_apply_bar",
        "ready_group_count": ready_groups,
        "blocked_group_count": blocked_groups,
        "embedding_count": embeddings,
        "confirmation_required": ready_groups > 0,
        "confirmation_acknowledged": bool(confirmation_acknowledged),
        "apply_enabled": enabled,
        "primary_label": "Apply ready people groups" if enabled else "Review before applying",
        "blocked_reason": None if enabled else "Confirmation and a clean apply preview are required.",
        "executes_immediately": False,
    }


__all__ = ["PEOPLE_APPLY_BAR_SCHEMA_VERSION", "build_people_apply_bar"]
