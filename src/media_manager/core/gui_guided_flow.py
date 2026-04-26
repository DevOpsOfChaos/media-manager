from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

GUIDED_FLOW_SCHEMA_VERSION = "1.0"


def build_guided_step(step_id: str, title: str, *, complete: bool = False, blocked: bool = False, optional: bool = False, details: str = "") -> dict[str, object]:
    return {
        "schema_version": GUIDED_FLOW_SCHEMA_VERSION,
        "kind": "guided_step",
        "step_id": step_id,
        "title": title,
        "complete": bool(complete),
        "blocked": bool(blocked),
        "optional": bool(optional),
        "details": details,
        "status": "blocked" if blocked else "complete" if complete else "pending",
    }


def build_guided_flow(flow_id: str, steps: Iterable[Mapping[str, Any]], *, title: str = "") -> dict[str, object]:
    step_list = [dict(step) for step in steps]
    current = next((step for step in step_list if not step.get("complete") and not step.get("optional")), None)
    if current is None:
        current = next((step for step in step_list if not step.get("complete")), None)
    return {
        "schema_version": GUIDED_FLOW_SCHEMA_VERSION,
        "kind": "guided_flow",
        "flow_id": flow_id,
        "title": title or flow_id.replace("_", " ").title(),
        "steps": step_list,
        "step_count": len(step_list),
        "complete_count": sum(1 for step in step_list if step.get("complete")),
        "blocked_count": sum(1 for step in step_list if step.get("blocked")),
        "current_step_id": current.get("step_id") if current else None,
        "complete": bool(step_list) and all(step.get("complete") or step.get("optional") for step in step_list),
    }


def build_people_review_guided_flow(*, has_scan_report: bool, has_bundle: bool, has_review_decisions: bool, has_apply_preview: bool, catalog_updated: bool = False) -> dict[str, object]:
    steps = [
        build_guided_step("scan", "Scan people", complete=has_scan_report),
        build_guided_step("bundle", "Build review bundle", complete=has_bundle, blocked=not has_scan_report),
        build_guided_step("review", "Curate people groups", complete=has_review_decisions, blocked=not has_bundle),
        build_guided_step("preview_apply", "Preview catalog update", complete=has_apply_preview, blocked=not has_review_decisions),
        build_guided_step("apply_catalog", "Apply to catalog", complete=catalog_updated, blocked=not has_apply_preview),
        build_guided_step("rescan", "Rescan to verify matches", complete=False, optional=True, blocked=not catalog_updated),
    ]
    return build_guided_flow("people_review", steps, title="People review workflow")


__all__ = ["GUIDED_FLOW_SCHEMA_VERSION", "build_guided_step", "build_guided_flow", "build_people_review_guided_flow"]
