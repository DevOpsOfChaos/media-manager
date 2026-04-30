from __future__ import annotations

from collections.abc import Mapping
from typing import Any

REVIEW_WORKBENCH_VIEW_MODEL_SCHEMA_VERSION = "1.1"
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


def _first_attention_lane(lanes: list[Mapping[str, Any]]) -> Mapping[str, Any]:
    return next((lane for lane in lanes if _as_int(lane.get("attention_count")) > 0), lanes[0] if lanes else {})


def _select_lane(lanes: list[Mapping[str, Any]], selected_lane_id: str | None) -> Mapping[str, Any]:
    requested = str(selected_lane_id or "").strip()
    if requested:
        match = next((lane for lane in lanes if str(lane.get("lane_id") or "") == requested), None)
        if match is not None:
            return match
    return _first_attention_lane(lanes)


def _navigation_target_page_id(selected_lane: Mapping[str, Any]) -> str:
    action = _as_mapping(selected_lane.get("primary_action"))
    return str(action.get("page_id") or selected_lane.get("page_id") or "")


def build_review_workbench_toolbar(selected_lane: Mapping[str, Any], lanes: list[Mapping[str, Any]]) -> dict[str, object]:
    lane_id = str(selected_lane.get("lane_id") or "")
    navigation_target = _navigation_target_page_id(selected_lane)
    has_selection = bool(lane_id)
    return {
        "kind": "ui_review_workbench_toolbar",
        "selected_lane_id": lane_id or None,
        "action_count": 3,
        "executes_commands": False,
        "actions": [
            {
                "id": "open-selected-lane",
                "label": "Open selected lane" if has_selection else "Select a lane",
                "enabled": has_selection,
                "page_id": navigation_target or None,
                "executes_immediately": False,
            },
            {
                "id": "refresh-review-workbench",
                "label": "Refresh workbench",
                "enabled": True,
                "page_id": "review-workbench",
                "executes_immediately": False,
            },
            {
                "id": "apply-reviewed-decisions",
                "label": "Apply reviewed decisions",
                "enabled": False,
                "page_id": navigation_target or None,
                "executes_immediately": False,
                "requires_explicit_user_confirmation": True,
            },
        ],
        "available_lane_ids": [str(lane.get("lane_id") or "") for lane in lanes if lane.get("lane_id")],
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


def build_review_workbench_selection_options(lanes: list[Mapping[str, Any]]) -> list[dict[str, object]]:
    options: list[dict[str, object]] = []
    for lane in lanes:
        lane_id = str(lane.get("lane_id") or "")
        if not lane_id:
            continue
        attention_count = _as_int(lane.get("attention_count"))
        item_count = _as_int(lane.get("item_count"))
        options.append(
            {
                "id": lane_id,
                "label": str(lane.get("title") or lane_id),
                "page_id": str(lane.get("page_id") or "") or None,
                "status": str(lane.get("status") or "empty"),
                "attention_count": attention_count,
                "item_count": item_count,
                "has_attention": attention_count > 0,
                "enabled": True,
                "executes_immediately": False,
            }
        )
    return options


def build_review_workbench_lane_filter(
    lanes: list[Mapping[str, Any]],
    *,
    status: str = "all",
    query: str = "",
) -> dict[str, object]:
    normalized_status = str(status or "all").strip().lower().replace("-", "_") or "all"
    if normalized_status not in {"all", "needs_review", "ready", "empty"}:
        normalized_status = "all"
    normalized_query = str(query or "").strip().lower()
    return {
        "kind": "ui_review_workbench_lane_filter",
        "status": normalized_status,
        "query": normalized_query,
        "available_statuses": ["all", "needs_review", "ready", "empty"],
        "lane_count": len(lanes),
        "attention_lane_ids": [str(lane.get("lane_id") or "") for lane in lanes if _as_int(lane.get("attention_count")) > 0],
        "executes_commands": False,
    }


def filter_review_workbench_lanes(
    lanes: list[Mapping[str, Any]],
    *,
    status: str = "all",
    query: str = "",
) -> list[dict[str, object]]:
    filter_model = build_review_workbench_lane_filter(lanes, status=status, query=query)
    wanted_status = str(filter_model["status"])
    wanted_query = str(filter_model["query"])
    filtered: list[dict[str, object]] = []
    for lane in lanes:
        lane_status = str(lane.get("status") or "empty")
        if wanted_status != "all" and lane_status != wanted_status:
            continue
        searchable = " ".join(
            str(part or "")
            for part in (
                lane.get("lane_id"),
                lane.get("title"),
                lane.get("description"),
                lane.get("page_id"),
                lane_status,
            )
        ).lower()
        if wanted_query and wanted_query not in searchable:
            continue
        filtered.append(dict(lane))
    return filtered


def build_ui_review_workbench_view_model(
    *,
    duplicate_review: Mapping[str, Any],
    similar_images: Mapping[str, Any],
    decision_summary: Mapping[str, Any],
    people_review_summary: Mapping[str, Any] | None = None,
    selected_lane_id: str | None = None,
    lane_status_filter: str = "all",
    lane_query: str = "",
) -> dict[str, object]:
    lanes = build_review_workbench_lanes(
        duplicate_review=duplicate_review,
        similar_images=similar_images,
        decision_summary=decision_summary,
        people_review_summary=people_review_summary,
    )
    lane_maps: list[Mapping[str, Any]] = lanes
    selected_lane = _select_lane(lane_maps, selected_lane_id)
    attention_count = sum(_as_int(lane.get("attention_count")) for lane in lanes)
    item_count = sum(_as_int(lane.get("item_count")) for lane in lanes)
    selected_lane_dict = dict(selected_lane) if selected_lane else None
    available_lane_ids = [str(lane.get("lane_id") or "") for lane in lanes if lane.get("lane_id")]
    attention_lane_ids = [str(lane.get("lane_id") or "") for lane in lanes if _as_int(lane.get("attention_count")) > 0]
    selected_latest_run_path = str(selected_lane.get("latest_run_path") or "") if selected_lane else ""
    navigation_target_page_id = _navigation_target_page_id(selected_lane)
    toolbar = build_review_workbench_toolbar(selected_lane, lane_maps)
    lane_filter = build_review_workbench_lane_filter(lane_maps, status=lane_status_filter, query=lane_query)
    filtered_lanes = filter_review_workbench_lanes(lane_maps, status=lane_status_filter, query=lane_query)
    selection_options = build_review_workbench_selection_options(lane_maps)
    return {
        "schema_version": REVIEW_WORKBENCH_VIEW_MODEL_SCHEMA_VERSION,
        "kind": REVIEW_WORKBENCH_VIEW_MODEL_KIND,
        "title": "Review workbench",
        "description": "One UI entry point for duplicate, similar-image, people, and apply-readiness review queues.",
        "active_lane_id": selected_lane.get("lane_id") if selected_lane else None,
        "selected_lane_id": selected_lane.get("lane_id") if selected_lane else None,
        "selected_lane": selected_lane_dict,
        "available_lane_ids": available_lane_ids,
        "attention_lane_ids": attention_lane_ids,
        "navigation_target_page_id": navigation_target_page_id or None,
        "latest_run_path": selected_latest_run_path,
        "primary_action": dict(_as_mapping(selected_lane.get("primary_action"))) if selected_lane else None,
        "toolbar": toolbar,
        "lane_filter": lane_filter,
        "filtered_lanes": filtered_lanes,
        "selection_options": selection_options,
        "lanes": lanes,
        "summary": {
            "lane_count": len(lanes),
            "item_count": item_count,
            "attention_count": attention_count,
            "attention_lane_count": len(attention_lane_ids),
            "filtered_lane_count": len(filtered_lanes),
            "selection_option_count": len(selection_options),
            "selected_lane_id": selected_lane.get("lane_id") if selected_lane else None,
            "navigation_target_page_id": navigation_target_page_id or None,
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
    "build_review_workbench_lane_filter",
    "build_review_workbench_lanes",
    "build_review_workbench_selection_options",
    "build_review_workbench_toolbar",
    "filter_review_workbench_lanes",
    "build_ui_review_workbench_view_model",
]
