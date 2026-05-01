from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

from .gui_review_workbench_controller import build_review_workbench_update_intent, reduce_review_workbench_state

REVIEW_WORKBENCH_STATEFUL_REBUILD_SCHEMA_VERSION = "1.0"
REVIEW_WORKBENCH_STATEFUL_REBUILD_KIND = "ui_review_workbench_stateful_rebuild_bundle"
REVIEW_WORKBENCH_STATEFUL_REBUILD_LOOP_KIND = "ui_review_workbench_stateful_rebuild_loop"

_STATE_ACTIONS = {
    "select_lane",
    "set_filter",
    "set_query",
    "set_sort",
    "set_page",
    "set_page_size",
    "reset_view",
    "refresh_view",
}


_DEF_ARTIFACT_NAMES = (
    "review_workbench_stateful_rebuild.json",
    "review_workbench_rebuild_transition.json",
    "review_workbench_next_service_bundle.json",
    "review_workbench_next_page_state.json",
    "review_workbench_next_interaction_plan.json",
)


def _now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _as_mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _as_list(value: object) -> list[Any]:
    return value if isinstance(value, list) else []


def _as_int(value: object, default: int = 0) -> int:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    try:
        return int(str(value))
    except (TypeError, ValueError):
        return default


def _text(value: object, fallback: str = "") -> str:
    if value is None:
        return fallback
    text = str(value).strip()
    return text or fallback


def _state_from_service(service_bundle: Mapping[str, Any]) -> dict[str, object]:
    controller_state = _as_mapping(service_bundle.get("controller_state"))
    state = _as_mapping(controller_state.get("state"))
    if state:
        return {
            "selected_lane_id": state.get("selected_lane_id"),
            "lane_status_filter": str(state.get("lane_status_filter") or "all"),
            "lane_query": str(state.get("lane_query") or ""),
            "lane_sort_mode": str(state.get("lane_sort_mode") or "attention_first"),
            "page": _as_int(state.get("page"), 1),
            "page_size": _as_int(state.get("page_size"), 20),
        }
    view_model = _as_mapping(service_bundle.get("view_model"))
    table_model = _as_mapping(service_bundle.get("table_model"))
    lane_filter = _as_mapping(view_model.get("lane_filter"))
    lane_sort = _as_mapping(view_model.get("lane_sort"))
    pagination = _as_mapping(table_model.get("pagination"))
    return {
        "selected_lane_id": view_model.get("selected_lane_id"),
        "lane_status_filter": str(lane_filter.get("status") or "all"),
        "lane_query": str(lane_filter.get("query") or ""),
        "lane_sort_mode": str(lane_sort.get("mode") or "attention_first"),
        "page": _as_int(pagination.get("page"), 1),
        "page_size": _as_int(pagination.get("page_size"), 20),
    }


def _lane_by_id(service_bundle: Mapping[str, Any], lane_id: str) -> Mapping[str, Any]:
    view_model = _as_mapping(service_bundle.get("view_model"))
    for lane in _as_list(view_model.get("lanes")):
        lane_map = _as_mapping(lane)
        if str(lane_map.get("lane_id") or "") == lane_id:
            return lane_map
    return {}


def _source_from_lane(lane: Mapping[str, Any], *, fallback_kind: str) -> dict[str, object]:
    item_count = _as_int(lane.get("item_count"), 0)
    attention_count = _as_int(lane.get("attention_count"), 0)
    latest_run_path = _text(lane.get("latest_run_path"))
    payload: dict[str, object] = {
        "kind": fallback_kind,
        "run_count": item_count,
        "review_candidate_count": attention_count,
        "error_count": 0,
    }
    if latest_run_path:
        payload["latest_run"] = {"path": latest_run_path}
    return payload


def _people_summary_from_lane(lane: Mapping[str, Any]) -> dict[str, object]:
    item_count = _as_int(lane.get("item_count"), 0)
    attention_count = _as_int(lane.get("attention_count"), 0)
    return {
        "kind": "recovered_people_review_summary",
        "group_count": attention_count if attention_count > 0 else item_count,
        "face_count": item_count,
        "ready_for_gui": item_count > 0,
    }


def _source_inputs_from_service(service_bundle: Mapping[str, Any]) -> dict[str, object]:
    duplicates = _lane_by_id(service_bundle, "duplicates")
    similar = _lane_by_id(service_bundle, "similar-images")
    decisions = _lane_by_id(service_bundle, "decision-summary")
    people = _lane_by_id(service_bundle, "people-review")
    service_inputs = _as_mapping(service_bundle.get("inputs"))
    return {
        "duplicate_review": _source_from_lane(duplicates, fallback_kind="recovered_duplicate_review_summary"),
        "similar_images": _source_from_lane(similar, fallback_kind="recovered_similar_images_summary"),
        "decision_summary": {
            **_source_from_lane(decisions, fallback_kind="recovered_decision_summary"),
            "error_count": _as_int(decisions.get("attention_count"), 0),
        },
        "people_review_summary": _people_summary_from_lane(people),
        "people_bundle_dir": service_inputs.get("people_bundle_dir"),
    }


def normalize_review_workbench_rebuild_intent(intent: Mapping[str, Any] | None = None, **overrides: Any) -> dict[str, object]:
    raw = _as_mapping(intent)
    action = _text(overrides.get("action", raw.get("action")), "refresh_view").lower().replace("-", "_")
    if action not in _STATE_ACTIONS and action not in {"open_selected_lane", "disabled_apply"}:
        action = "refresh_view"
    lane_id = overrides.get("lane_id", raw.get("lane_id"))
    status = overrides.get("status", raw.get("status"))
    query = overrides.get("query", raw.get("query"))
    sort_mode = overrides.get("sort_mode", raw.get("sort_mode"))
    page = overrides.get("page", raw.get("page"))
    page_size = overrides.get("page_size", raw.get("page_size"))
    return build_review_workbench_update_intent(
        action,
        lane_id=_text(lane_id) or None,
        status=_text(status) or None,
        query=str(query or ""),
        sort_mode=_text(sort_mode) or None,
        page=_as_int(page, 0) if page is not None else None,
        page_size=_as_int(page_size, 0) if page_size is not None else None,
    )


def build_review_workbench_stateful_rebuild_loop_contract(service_bundle: Mapping[str, Any]) -> dict[str, object]:
    """Describe the non-executing stateful rebuild loop a GUI may call after UI intents."""

    interaction_plan = _as_mapping(service_bundle.get("interaction_plan"))
    intents = [_as_mapping(item) for item in _as_list(interaction_plan.get("intent_catalog")) if isinstance(item, Mapping)]
    stateful_intents = [intent for intent in intents if str(intent.get("action") or "") in _STATE_ACTIONS]
    current_state = _state_from_service(service_bundle)
    readiness_checks = [
        {
            "id": "service-state-present",
            "label": "Current Review Workbench state is available for reducer input",
            "ok": bool(current_state),
        },
        {
            "id": "stateful-intents-present",
            "label": "Interaction plan exposes state-changing intents",
            "ok": bool(stateful_intents),
        },
        {
            "id": "non-executing-intents",
            "label": "All stateful intents are non-executing",
            "ok": all(intent.get("executes_commands") is False for intent in stateful_intents),
        },
        {
            "id": "service-non-executing",
            "label": "Source service bundle does not execute commands",
            "ok": _as_mapping(service_bundle.get("capabilities")).get("executes_commands") is False,
        },
    ]
    failed = [check for check in readiness_checks if check.get("ok") is not True]
    return {
        "schema_version": REVIEW_WORKBENCH_STATEFUL_REBUILD_SCHEMA_VERSION,
        "kind": REVIEW_WORKBENCH_STATEFUL_REBUILD_LOOP_KIND,
        "page_id": "review-workbench",
        "current_state": current_state,
        "supported_actions": sorted(_STATE_ACTIONS),
        "stateful_intent_count": len(stateful_intents),
        "stateful_intent_kinds": [str(intent.get("intent_kind") or intent.get("action") or "") for intent in stateful_intents],
        "request_schema": {
            "action": sorted(_STATE_ACTIONS),
            "lane_id": "optional lane id for select_lane",
            "status": "optional status for set_filter",
            "query": "optional filter query for set_query",
            "sort_mode": "optional sort mode for set_sort",
            "page": "optional positive page number for set_page",
            "page_size": "optional positive page size for set_page_size",
        },
        "response_artifacts": list(_DEF_ARTIFACT_NAMES),
        "capabilities": {
            "headless_testable": True,
            "requires_pyside6": False,
            "opens_window": False,
            "executes_commands": False,
            "executes_media_operations": False,
            "rebuilds_view_state": True,
            "writes_app_state": False,
            "apply_enabled": False,
        },
        "readiness": {
            "ready": not failed,
            "status": "ready" if not failed else "blocked",
            "failed_check_count": len(failed),
            "checks": readiness_checks,
            "next_action": (
                "Dispatch GUI intents to review-workbench-stateful-rebuild and replace the page state with its next_page_state payload."
                if not failed
                else "Fix the Review Workbench interaction/service state before wiring live GUI rebuilds."
            ),
        },
        "summary": {
            "stateful_intent_count": len(stateful_intents),
            "current_selected_lane_id": current_state.get("selected_lane_id"),
            "current_lane_status_filter": current_state.get("lane_status_filter"),
            "current_lane_query": current_state.get("lane_query"),
            "current_lane_sort_mode": current_state.get("lane_sort_mode"),
            "ready": not failed,
            "status": "ready" if not failed else "blocked",
        },
    }


def build_review_workbench_page_state_from_service(service_bundle: Mapping[str, Any]) -> dict[str, object]:
    """Build a Qt-consumable page-state payload from a rebuilt service bundle."""

    summary = _as_mapping(service_bundle.get("summary"))
    return {
        "schema_version": REVIEW_WORKBENCH_STATEFUL_REBUILD_SCHEMA_VERSION,
        "kind": "ui_review_workbench_rebuilt_page_state",
        "page_id": "review-workbench",
        "title": "Review Workbench",
        "description": "Rebuilt Review Workbench page state after a local UI intent.",
        "layout": "review_workbench_table_detail",
        "workbench_service": dict(service_bundle),
        "view_model": _as_mapping(service_bundle.get("view_model")),
        "table_model": _as_mapping(service_bundle.get("table_model")),
        "action_plan": _as_mapping(service_bundle.get("action_plan")),
        "qt_adapter_package": _as_mapping(service_bundle.get("qt_adapter_package")),
        "qt_widget_binding_plan": _as_mapping(service_bundle.get("qt_widget_binding_plan")),
        "qt_widget_skeleton": _as_mapping(service_bundle.get("qt_widget_skeleton")),
        "interaction_plan": _as_mapping(service_bundle.get("interaction_plan")),
        "callback_mount_plan": _as_mapping(service_bundle.get("callback_mount_plan")),
        "apply_preview": _as_mapping(service_bundle.get("apply_preview")),
        "confirmation_dialog": _as_mapping(service_bundle.get("confirmation_dialog")),
        "apply_executor_contract": _as_mapping(service_bundle.get("apply_executor_contract")),
        "executor_handoff_panel": _as_mapping(service_bundle.get("executor_handoff_panel")),
        "stateful_rebuild_loop": _as_mapping(service_bundle.get("stateful_rebuild_loop")),
        "summary": dict(summary),
        "capabilities": {
            "headless_testable": True,
            "requires_pyside6": False,
            "opens_window": False,
            "executes_commands": False,
            "executes_media_operations": False,
            "apply_enabled": False,
        },
        "readiness": _as_mapping(service_bundle.get("readiness")),
    }


def build_review_workbench_stateful_rebuild_bundle(
    service_bundle: Mapping[str, Any],
    intent: Mapping[str, Any] | None = None,
    *,
    duplicate_review: Mapping[str, Any] | None = None,
    similar_images: Mapping[str, Any] | None = None,
    decision_summary: Mapping[str, Any] | None = None,
    people_review_summary: Mapping[str, Any] | None = None,
    people_bundle_dir: str | Path | None = None,
    reviewed_decision_plan: Mapping[str, Any] | None = None,
) -> dict[str, object]:
    """Apply one local UI intent and rebuild the full non-executing page bundle."""

    current_state = _state_from_service(service_bundle)
    normalized_intent = normalize_review_workbench_rebuild_intent(intent)
    reduced = reduce_review_workbench_state(current_state, normalized_intent)
    next_state = _as_mapping(reduced.get("state"))
    recovered_inputs = _source_inputs_from_service(service_bundle)
    effective_people_bundle_dir = people_bundle_dir if people_bundle_dir is not None else recovered_inputs.get("people_bundle_dir")

    # Lazy import avoids a top-level cycle: the service bundle embeds the loop contract,
    # while this full rebuild function uses the service builder to produce the next state.
    from .gui_review_workbench_service import build_gui_review_workbench_service_bundle

    service_kwargs = {
        "duplicate_review": duplicate_review or _as_mapping(recovered_inputs.get("duplicate_review")),
        "similar_images": similar_images or _as_mapping(recovered_inputs.get("similar_images")),
        "decision_summary": decision_summary or _as_mapping(recovered_inputs.get("decision_summary")),
        "people_review_summary": people_review_summary or _as_mapping(recovered_inputs.get("people_review_summary")),
        "people_bundle_dir": effective_people_bundle_dir if isinstance(effective_people_bundle_dir, (str, Path)) else None,
        "reviewed_decision_plan": reviewed_decision_plan,
        "selected_lane_id": _text(next_state.get("selected_lane_id")) or None,
        "lane_status_filter": str(next_state.get("lane_status_filter") or "all"),
        "lane_query": str(next_state.get("lane_query") or ""),
        "lane_sort_mode": str(next_state.get("lane_sort_mode") or "attention_first"),
        "page": _as_int(next_state.get("page"), 1),
        "page_size": _as_int(next_state.get("page_size"), 20),
    }
    next_service = build_gui_review_workbench_service_bundle(**service_kwargs)
    next_view = _as_mapping(next_service.get("view_model"))
    filtered_ids = [
        str(_as_mapping(lane).get("lane_id") or "")
        for lane in _as_list(next_view.get("sorted_filtered_lanes"))
        if _as_mapping(lane).get("lane_id")
    ]
    selected_after_filter = str(next_view.get("selected_lane_id") or "")
    selection_rebased = False
    if filtered_ids and selected_after_filter not in filtered_ids:
        service_kwargs["selected_lane_id"] = filtered_ids[0]
        next_state = {**dict(next_state), "selected_lane_id": filtered_ids[0]}
        next_service = build_gui_review_workbench_service_bundle(**service_kwargs)
        selection_rebased = True
    next_page_state = build_review_workbench_page_state_from_service(next_service)
    transition = {
        "kind": "ui_review_workbench_rebuild_transition",
        "page_id": "review-workbench",
        "current_state": current_state,
        "intent": normalized_intent,
        "reduced_state": dict(next_state),
        "changed": bool(reduced.get("changed")) or selection_rebased,
        "selection_rebased": selection_rebased,
        "rebuild_required": True,
        "executes_commands": False,
        "executes_media_operations": False,
    }
    readiness_checks = [
        {
            "id": "intent-non-executing",
            "label": "Incoming intent is non-executing",
            "ok": normalized_intent.get("executes_commands") is False,
        },
        {
            "id": "state-reduced",
            "label": "Reducer produced a valid next state",
            "ok": bool(next_state),
        },
        {
            "id": "next-service-ready",
            "label": "Rebuilt Review Workbench service is ready",
            "ok": bool(_as_mapping(next_service.get("readiness")).get("ready")),
        },
        {
            "id": "next-service-non-executing",
            "label": "Rebuilt service still executes no commands",
            "ok": _as_mapping(next_service.get("capabilities")).get("executes_commands") is False,
        },
        {
            "id": "page-state-non-executing",
            "label": "Rebuilt page state is safe for Qt replacement",
            "ok": _as_mapping(next_page_state.get("capabilities")).get("executes_commands") is False,
        },
    ]
    failed = [check for check in readiness_checks if check.get("ok") is not True]
    summary = _as_mapping(next_service.get("summary"))
    return {
        "schema_version": REVIEW_WORKBENCH_STATEFUL_REBUILD_SCHEMA_VERSION,
        "kind": REVIEW_WORKBENCH_STATEFUL_REBUILD_KIND,
        "generated_at_utc": _now_utc(),
        "page_id": "review-workbench",
        "transition": transition,
        "current_service_summary": _as_mapping(service_bundle.get("summary")),
        "next_service_summary": summary,
        "next_service_bundle": next_service,
        "next_page_state": next_page_state,
        "render_update": {
            "strategy": "replace_review_workbench_page_state",
            "replace_page_id": "review-workbench",
            "preserve_desktop_shell": True,
            "requires_pyside6": False,
            "opens_window": False,
            "executes_commands": False,
        },
        "capabilities": {
            "headless_testable": True,
            "requires_pyside6": False,
            "opens_window": False,
            "executes_commands": False,
            "executes_media_operations": False,
            "writes_app_state": False,
            "apply_enabled": False,
        },
        "readiness": {
            "ready": not failed,
            "status": "ready" if not failed else "blocked",
            "failed_check_count": len(failed),
            "checks": readiness_checks,
            "next_action": (
                "Replace the Review Workbench page state and re-render the existing Qt widget tree."
                if not failed
                else "Do not replace the visible page until rebuild checks pass."
            ),
        },
        "summary": {
            "changed": bool(reduced.get("changed")) or selection_rebased,
            "selection_rebased": selection_rebased,
            "intent_action": normalized_intent.get("action"),
            "selected_lane_id": summary.get("selected_lane_id"),
            "lane_count": summary.get("lane_count", 0),
            "table_row_count": summary.get("table_row_count", 0),
            "apply_preview_status": summary.get("apply_preview_status"),
            "confirmation_dialog_status": summary.get("confirmation_dialog_status"),
            "executor_handoff_panel_status": summary.get("executor_handoff_panel_status"),
            "executes_commands": False,
            "ready": not failed,
            "status": "ready" if not failed else "blocked",
        },
        "artifact_names": list(_DEF_ARTIFACT_NAMES),
    }


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(dict(payload), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_review_workbench_stateful_rebuild_bundle(
    out_dir: str | Path,
    service_bundle: Mapping[str, Any],
    intent: Mapping[str, Any] | None = None,
    **kwargs: Any,
) -> dict[str, object]:
    root = Path(out_dir)
    root.mkdir(parents=True, exist_ok=True)
    bundle = build_review_workbench_stateful_rebuild_bundle(service_bundle, intent, **kwargs)
    files: list[tuple[str, Mapping[str, Any]]] = [
        ("review_workbench_stateful_rebuild.json", bundle),
        ("review_workbench_rebuild_transition.json", _as_mapping(bundle.get("transition"))),
        ("review_workbench_next_service_bundle.json", _as_mapping(bundle.get("next_service_bundle"))),
        ("review_workbench_next_page_state.json", _as_mapping(bundle.get("next_page_state"))),
        (
            "review_workbench_next_interaction_plan.json",
            _as_mapping(_as_mapping(bundle.get("next_service_bundle")).get("interaction_plan")),
        ),
    ]
    written_files: list[str] = []
    for name, payload in files:
        path = root / name
        _write_json(path, payload)
        written_files.append(str(path))
    readme = root / "README.txt"
    readme.write_text(
        "Review Workbench stateful rebuild bundle\n"
        "Applies one local UI intent to the current Review Workbench state and writes the next non-executing page-state artifacts.\n"
        "This bundle does not import PySide6, open windows, write app state, execute commands, or perform media operations.\n",
        encoding="utf-8",
    )
    written_files.append(str(readme))
    return {**bundle, "output_dir": str(root), "written_files": written_files, "written_file_count": len(written_files)}


__all__ = [
    "REVIEW_WORKBENCH_STATEFUL_REBUILD_KIND",
    "REVIEW_WORKBENCH_STATEFUL_REBUILD_LOOP_KIND",
    "REVIEW_WORKBENCH_STATEFUL_REBUILD_SCHEMA_VERSION",
    "build_review_workbench_page_state_from_service",
    "build_review_workbench_stateful_rebuild_bundle",
    "build_review_workbench_stateful_rebuild_loop_contract",
    "normalize_review_workbench_rebuild_intent",
    "write_review_workbench_stateful_rebuild_bundle",
]
