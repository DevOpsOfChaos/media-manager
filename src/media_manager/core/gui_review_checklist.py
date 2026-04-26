from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

REVIEW_CHECKLIST_SCHEMA_VERSION = "1.0"


def build_check_item(item_id: str, label: str, *, passed: bool, severity: str = "info", details: str = "") -> dict[str, object]:
    return {
        "schema_version": REVIEW_CHECKLIST_SCHEMA_VERSION,
        "kind": "review_check_item",
        "item_id": item_id,
        "label": label,
        "passed": bool(passed),
        "severity": severity,
        "details": details,
    }


def build_review_checklist(items: Iterable[Mapping[str, Any]]) -> dict[str, object]:
    item_list = [dict(item) for item in items]
    failed = [item for item in item_list if not item.get("passed")]
    return {
        "schema_version": REVIEW_CHECKLIST_SCHEMA_VERSION,
        "kind": "review_checklist",
        "items": item_list,
        "item_count": len(item_list),
        "passed_count": sum(1 for item in item_list if item.get("passed")),
        "failed_count": len(failed),
        "ready": not failed,
        "blocking_count": sum(1 for item in failed if item.get("severity") in {"error", "warning"}),
    }


def people_review_apply_checklist(*, ready_group_count: int, has_encodings: bool, problem_count: int = 0, privacy_acknowledged: bool = False) -> dict[str, object]:
    return build_review_checklist(
        [
            build_check_item("ready_groups", "At least one group is ready", passed=ready_group_count > 0, severity="warning"),
            build_check_item("encodings", "Report contains face encodings", passed=has_encodings, severity="error"),
            build_check_item("no_problems", "No blocking problems", passed=problem_count == 0, severity="error"),
            build_check_item("privacy", "People data privacy acknowledged", passed=privacy_acknowledged, severity="warning"),
        ]
    )


__all__ = ["REVIEW_CHECKLIST_SCHEMA_VERSION", "build_check_item", "build_review_checklist", "people_review_apply_checklist"]
