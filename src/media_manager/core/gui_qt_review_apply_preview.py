from __future__ import annotations

from collections.abc import Mapping
from typing import Any

REVIEW_APPLY_PREVIEW_SCHEMA_VERSION = "1.0"


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def build_qt_review_apply_preview(workbench_state: Mapping[str, Any]) -> dict[str, Any]:
    page = _as_mapping(workbench_state.get("page"))
    queue = _as_mapping(page.get("queue"))
    groups = [item for item in _as_list(queue.get("groups") or page.get("groups")) if isinstance(item, Mapping)]
    changes = [item for item in _as_list(workbench_state.get("pending_changes")) if isinstance(item, Mapping)]
    ready_groups = [group for group in groups if str(group.get("status")) in {"ready", "ready_to_apply", "named_not_applied"}]
    needs_name = [group for group in groups if str(group.get("status")) == "needs_name"]
    high_risk_changes = [change for change in changes if change.get("requires_confirmation")]
    blocked_reasons: list[str] = []
    if not ready_groups:
        blocked_reasons.append("no_ready_groups")
    if needs_name:
        blocked_reasons.append("groups_need_name")
    if high_risk_changes:
        blocked_reasons.append("confirmation_required")
    return {
        "schema_version": REVIEW_APPLY_PREVIEW_SCHEMA_VERSION,
        "kind": "qt_review_apply_preview",
        "ready_group_count": len(ready_groups),
        "needs_name_group_count": len(needs_name),
        "pending_change_count": len(changes),
        "requires_confirmation_count": len(high_risk_changes),
        "blocked_reasons": blocked_reasons,
        "safe_to_apply": bool(ready_groups) and not needs_name and not high_risk_changes,
        "executes_immediately": False,
    }


__all__ = ["REVIEW_APPLY_PREVIEW_SCHEMA_VERSION", "build_qt_review_apply_preview"]
