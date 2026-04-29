from __future__ import annotations

from collections.abc import Mapping
from typing import Any

REVIEW_WORKBENCH_VIEW_MODEL_SCHEMA_VERSION = "1.0"
REVIEW_WORKBENCH_VIEW_MODEL_KIND = "ui_review_workbench_view_model"


def _as_mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _as_int(value: object, default: int = 0) -> int:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    try:
        return int(str(value))
    except (TypeError, ValueError):
        return default


def _latest_run_path(model: Mapping[str, Any]) -> str:
    latest = _as_mapping(model.get("latest_run"))
    return str(latest.get("path") or "")


def _build_lane(
    lane_id: str,
    *,
    title: str,
    description: str,
    page_id: str,
    source_model: Mapping[str, Any],
    item_count: int,
    attention_count: int = 0,
    empty_state: str = "",
) -> dict[str, object]:
    status = "needs_review" if attention_count > 0 else "ready" if item_count > 0 else "empty"
    return {
        "kind": "ui_review_workbench_lane",
        "lane_id": lane_id,
        "title": title,
        "description": description,
        "page_id": page_id,
        "status": status,
        "item_count": max(0, int(item_count)),
        "attention_count": max(0, int(attention_count)),
        "latest_run_path": _latest_run_path(source_model),
        "empty_state": empty_state if item_count <= 0 else None,
        "primary_action": {
            "id": f"open-{lane_id}",
            "label": f"Open {title}",
            "page_id": page_id,
            "executes_immediately": False,
        },
        "apply_enabled": False,
        "executes_commands": False,
    }


def build_review_workbench_lanes(
    *,
    duplicate_review: Mapping[str, Any],
    similar_images: Mapping[str, Any],
    decision_summary: Mapping[str, Any],
    people_review_summary: Mapping[str, Any] | None = None,
) -> list[dict[str, object]]:
    people_summary = _as_mapping(people_review_summary)
    duplicate_candidates = _as_int(duplicate_review.get("review_candidate_count"))
    similar_candidates = _as_int(similar_images.get("review_candidate_count"))
    people_groups = _as_int(people_summary.get("group_count", people_summary.get("groups")))
    people_faces = _as_int(people_summary.get("face_count", people_summary.get("faces")))
    decision_errors = _as_int(decision_summary.get("error_count"))
    decision_candidates = _as_int(decision_summary.get("review_candidate_count"))
    return [
        _build_lane(
            "duplicates",
            title="Duplicate review",
            description="Resolve exact duplicate groups before destructive apply steps are enabled.",
            page_id="run-history",
            source_model=duplicate_review,
            item_count=max(duplicate_candidates, _as_int(duplicate_review.get("run_count"))),
            attention_count=duplicate_candidates,
            empty_state="Run a duplicate preview to populate this lane.",
        ),
        _build_lane(
            "similar-images",
            title="Similar images",
            description="Review visually similar image groups and keep/delete decisions.",
            page_id="run-history",
            source_model=similar_images,
            item_count=max(similar_candidates, _as_int(similar_images.get("run_count"))),
            attention_count=similar_candidates,
            empty_state="Run a similar-images preview to populate this lane.",
        ),
        _build_lane(
            "people-review",
            title="People review",
            description="Review local face groups and naming decisions without uploading media.",
            page_id="people-review",
            source_model={},
            item_count=max(people_groups, people_faces),
            attention_count=people_groups,
            empty_state="Create or load a people review bundle to populate this lane.",
        ),
        _build_lane(
            "decision-summary",
            title="Decision summary",
            description="Check blockers before apply actions are surfaced.",
            page_id="run-history",
            source_model=decision_summary,
            item_count=max(decision_candidates, decision_errors),
            attention_count=decision_candidates + decision_errors,
            empty_state="No pending review blockers are visible.",
        ),
    ]


def build_ui_review_workbench_view_model(
    *,
    duplicate_review: Mapping[str, Any],
    similar_images: Mapping[str, Any],
    decision_summary: Mapping[str, Any],
    people_review_summary: Mapping[str, Any] | None = None,
) -> dict[str, object]:
    lanes = build_review_workbench_lanes(
        duplicate_review=duplicate_review,
        similar_images=similar_images,
        decision_summary=decision_summary,
        people_review_summary=people_review_summary,
    )
    attention_count = sum(_as_int(lane.get("attention_count")) for lane in lanes)
    item_count = sum(_as_int(lane.get("item_count")) for lane in lanes)
    active_lane = next((lane for lane in lanes if _as_int(lane.get("attention_count")) > 0), lanes[0] if lanes else {})
    return {
        "schema_version": REVIEW_WORKBENCH_VIEW_MODEL_SCHEMA_VERSION,
        "kind": REVIEW_WORKBENCH_VIEW_MODEL_KIND,
        "title": "Review workbench",
        "description": "One UI entry point for duplicate, similar-image, people, and apply-readiness review queues.",
        "active_lane_id": active_lane.get("lane_id"),
        "lanes": lanes,
        "summary": {
            "lane_count": len(lanes),
            "item_count": item_count,
            "attention_count": attention_count,
            "blocked_apply_count": sum(1 for lane in lanes if lane.get("apply_enabled") is False and _as_int(lane.get("attention_count")) > 0),
            "status": "needs_review" if attention_count > 0 else "empty" if item_count <= 0 else "ready",
        },
        "capabilities": {
            "headless_testable": True,
            "requires_pyside6": False,
            "opens_window": False,
            "executes_commands": False,
            "local_only": True,
            "apply_enabled": False,
        },
    }


__all__ = [
    "REVIEW_WORKBENCH_VIEW_MODEL_KIND",
    "REVIEW_WORKBENCH_VIEW_MODEL_SCHEMA_VERSION",
    "build_review_workbench_lanes",
    "build_ui_review_workbench_view_model",
]
