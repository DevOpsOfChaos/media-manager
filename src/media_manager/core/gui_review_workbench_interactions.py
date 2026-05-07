from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
import json
from typing import Any

from .gui_review_workbench_controller import build_review_workbench_update_intent, reduce_review_workbench_state

REVIEW_WORKBENCH_INTERACTION_SCHEMA_VERSION = "1.0"
REVIEW_WORKBENCH_INTERACTION_KIND = "ui_review_workbench_interaction_plan"


_KIND_TO_ACTION: dict[str, str] = {
    "filter_query_changed": "set_query",
    "filter_status_changed": "set_filter",
    "sort_mode_changed": "set_sort",
    "lane_selected": "select_lane",
    "table_row_activated": "open_selected_lane",
    "toolbar_open_selected_lane": "open_selected_lane",
    "toolbar_reset_filters": "reset_view",
    "toolbar_refresh": "refresh_view",
    "toolbar_apply_reviewed_decisions": "disabled_apply",
}


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


def _state_from_service(service_bundle: Mapping[str, Any]) -> Mapping[str, Any]:
    controller = _as_mapping(service_bundle.get("controller_state"))
    return _as_mapping(controller.get("state"))


def _lane_ids(service_bundle: Mapping[str, Any]) -> list[str]:
    view_model = _as_mapping(service_bundle.get("view_model"))
    lane_ids = view_model.get("available_lane_ids")
    if isinstance(lane_ids, list):
        return [str(item) for item in lane_ids if str(item or "").strip()]
    lanes = _as_list(view_model.get("lanes"))
    return [str(_as_mapping(lane).get("lane_id")) for lane in lanes if str(_as_mapping(lane).get("lane_id") or "")]


def _find_action(action_plan: Mapping[str, Any], action_id: str) -> Mapping[str, Any]:
    for action in _as_list(action_plan.get("actions")):
        action_map = _as_mapping(action)
        if str(action_map.get("id") or "") == action_id:
            return action_map
    return {}


def build_review_workbench_interaction_intent(
    intent_kind: str,
    *,
    lane_id: str | None = None,
    status: str | None = None,
    query: str | None = None,
    sort_mode: str | None = None,
    page: int | None = None,
    page_size: int | None = None,
    action_id: str | None = None,
    target_page_id: str | None = None,
    enabled: bool = True,
    reason: str | None = None,
) -> dict[str, object]:
    """Build one local UI interaction intent for the Review Workbench.

    The intent is a GUI-local event contract. It does not execute CLI commands,
    file operations, media operations, or apply plans. Route-capable intents are
    still deferred to the desktop shell router.
    """

    normalized_kind = _text(intent_kind, "noop").lower().replace("-", "_")
    action = _KIND_TO_ACTION.get(normalized_kind, "noop")
    update_intent = build_review_workbench_update_intent(
        action,
        lane_id=lane_id,
        status=status,
        query=query,
        sort_mode=sort_mode,
        page=page,
        page_size=page_size,
    )
    return {
        **update_intent,
        "schema_version": REVIEW_WORKBENCH_INTERACTION_SCHEMA_VERSION,
        "kind": "ui_review_workbench_interaction_intent",
        "intent_kind": normalized_kind,
        "action_id": action_id,
        "target_page_id": target_page_id,
        "enabled": bool(enabled),
        "disabled_reason": reason if not enabled else None,
        "route_deferred": action in {"open_selected_lane"} and bool(target_page_id),
        "state_only": action in {"set_query", "set_filter", "set_sort", "select_lane", "set_page", "set_page_size", "reset_view", "refresh_view"},
        "requires_explicit_user_confirmation": action == "disabled_apply",
        "executes_immediately": False,
        "executes_commands": False,
        "opens_window": False,
        "requires_pyside6": False,
    }


def _intent_catalog(service_bundle: Mapping[str, Any]) -> list[dict[str, object]]:
    view_model = _as_mapping(service_bundle.get("view_model"))
    action_plan = _as_mapping(service_bundle.get("action_plan"))
    lane_filter = _as_mapping(view_model.get("lane_filter"))
    lane_sort = _as_mapping(view_model.get("lane_sort"))
    selected_lane_id = str(view_model.get("selected_lane_id") or "") or None
    target_page_id = str(view_model.get("navigation_target_page_id") or "") or None
    open_action = _find_action(action_plan, "open-selected-lane")
    apply_action = _find_action(action_plan, "apply-reviewed-decisions")
    return [
        build_review_workbench_interaction_intent(
            "filter_query_changed",
            query=str(lane_filter.get("query") or ""),
            action_id="filter-query-changed",
        ),
        build_review_workbench_interaction_intent(
            "filter_status_changed",
            status=str(lane_filter.get("status") or "all"),
            action_id="filter-status-changed",
        ),
        build_review_workbench_interaction_intent(
            "sort_mode_changed",
            sort_mode=str(lane_sort.get("mode") or "attention_first"),
            action_id="sort-mode-changed",
        ),
        build_review_workbench_interaction_intent(
            "lane_selected",
            lane_id=selected_lane_id,
            action_id="lane-selected",
        ),
        build_review_workbench_interaction_intent(
            "table_row_activated",
            lane_id=selected_lane_id,
            action_id="table-row-activated",
            target_page_id=target_page_id,
            enabled=bool(selected_lane_id and target_page_id),
            reason=None if selected_lane_id and target_page_id else "Select a lane before routing.",
        ),
        build_review_workbench_interaction_intent(
            "toolbar_open_selected_lane",
            lane_id=selected_lane_id,
            action_id="open-selected-lane",
            target_page_id=target_page_id,
            enabled=bool(open_action.get("enabled")),
            reason=None if open_action.get("enabled") else "No selected lane route is available.",
        ),
        build_review_workbench_interaction_intent(
            "toolbar_reset_filters",
            action_id="reset-review-filters",
            enabled=bool(_find_action(action_plan, "reset-review-filters").get("enabled")),
        ),
        build_review_workbench_interaction_intent(
            "toolbar_refresh",
            action_id="refresh-review-workbench",
            enabled=bool(_find_action(action_plan, "refresh-review-workbench").get("enabled", True)),
        ),
        build_review_workbench_interaction_intent(
            "toolbar_apply_reviewed_decisions",
            lane_id=selected_lane_id,
            action_id="apply-reviewed-decisions",
            target_page_id=target_page_id,
            enabled=False,
            reason=str(apply_action.get("disabled_reason") or "Apply remains disabled until a reviewed command plan exists."),
        ),
    ]


def _signal_bindings(service_bundle: Mapping[str, Any]) -> list[dict[str, object]]:
    skeleton = _as_mapping(service_bundle.get("qt_widget_skeleton"))
    wires = [wire for wire in _as_list(skeleton.get("signal_wiring")) if isinstance(wire, Mapping)]
    slot_to_intent = {
        "filter_query_changed": "filter_query_changed",
        "filter_status_changed": "filter_status_changed",
        "sort_changed": "sort_mode_changed",
        "selected_lane_changed": "lane_selected",
        "row_activated": "table_row_activated",
        "route_intent_requested": "toolbar_open_selected_lane",
        "refresh_requested": "toolbar_refresh",
        "primary_lane_action_requested": "toolbar_open_selected_lane",
    }
    bindings: list[dict[str, object]] = []
    for wire in wires:
        slot = str(wire.get("target_slot") or "")
        intent_kind = slot_to_intent.get(slot, slot_to_intent.get(slot.replace("-", "_"), "noop"))
        bindings.append(
            {
                "binding_id": f"interaction-binding:{wire.get('component_id')}:{slot or 'noop'}",
                "component_id": wire.get("component_id"),
                "qt_signal": wire.get("qt_signal"),
                "target_slot": slot,
                "intent_kind": intent_kind,
                "dispatch_strategy": "emit_local_interaction_intent",
                "executes_immediately": False,
                "executes_commands": False,
            }
        )
    return bindings


def _toolbar_bindings(service_bundle: Mapping[str, Any]) -> list[dict[str, object]]:
    action_plan = _as_mapping(service_bundle.get("action_plan"))
    result: list[dict[str, object]] = []
    for action in _as_list(action_plan.get("actions")):
        action_map = _as_mapping(action)
        action_id = str(action_map.get("id") or "")
        intent_kind = {
            "open-selected-lane": "toolbar_open_selected_lane",
            "reset-review-filters": "toolbar_reset_filters",
            "refresh-review-workbench": "toolbar_refresh",
            "apply-reviewed-decisions": "toolbar_apply_reviewed_decisions",
        }.get(action_id, "noop")
        result.append(
            {
                "binding_id": f"toolbar-interaction:{action_id or 'action'}",
                "component_id": "review-workbench-toolbar",
                "action_id": action_id,
                "label": action_map.get("label"),
                "intent_kind": intent_kind,
                "enabled": bool(action_map.get("enabled")),
                "target_page_id": action_map.get("page_id"),
                "lane_id": action_map.get("lane_id"),
                "requires_explicit_user_confirmation": bool(action_map.get("requires_explicit_user_confirmation")),
                "executes_immediately": False,
                "executes_commands": False,
            }
        )
    return result


def _state_transition_previews(service_bundle: Mapping[str, Any], intents: list[Mapping[str, Any]]) -> list[dict[str, object]]:
    current_state = _state_from_service(service_bundle)
    previews: list[dict[str, object]] = []
    for intent in intents:
        action = str(intent.get("action") or "noop")
        if action not in {"set_query", "set_filter", "set_sort", "select_lane", "set_page", "set_page_size", "reset_view", "refresh_view"}:
            continue
        reduced = reduce_review_workbench_state(current_state, intent)
        previews.append(
            {
                "preview_id": f"state-preview:{intent.get('intent_kind')}",
                "intent_kind": intent.get("intent_kind"),
                "action": action,
                "changed": reduced.get("changed"),
                "next_state": dict(_as_mapping(reduced.get("state"))),
                "executes_commands": False,
            }
        )
    return previews


def _route_previews(service_bundle: Mapping[str, Any]) -> list[dict[str, object]]:
    adapter = _as_mapping(service_bundle.get("qt_adapter_package"))
    previews: list[dict[str, object]] = []
    for intent in _as_list(adapter.get("route_intents")):
        intent_map = _as_mapping(intent)
        previews.append(
            {
                "preview_id": f"route-preview:{intent_map.get('action_id') or intent_map.get('intent_id')}",
                "action_id": intent_map.get("action_id"),
                "target_page_id": intent_map.get("target_page_id"),
                "lane_id": intent_map.get("lane_id"),
                "enabled": bool(intent_map.get("enabled")),
                "dispatch": "desktop_shell_route_request",
                "executes_immediately": False,
                "executes_commands": False,
            }
        )
    return previews


def _readiness(
    *,
    service_bundle: Mapping[str, Any],
    intent_catalog: list[Mapping[str, Any]],
    signal_bindings: list[Mapping[str, Any]],
    toolbar_bindings: list[Mapping[str, Any]],
    state_transitions: list[Mapping[str, Any]],
) -> dict[str, object]:
    intent_kinds = {str(intent.get("intent_kind")) for intent in intent_catalog}
    required_intents = {
        "filter_query_changed",
        "filter_status_changed",
        "sort_mode_changed",
        "lane_selected",
        "table_row_activated",
        "toolbar_open_selected_lane",
        "toolbar_reset_filters",
        "toolbar_refresh",
        "toolbar_apply_reviewed_decisions",
    }
    checks = [
        {
            "id": "service-ready",
            "label": "Review Workbench service is ready before interaction wiring",
            "ok": bool(_as_mapping(service_bundle.get("readiness")).get("ready")),
        },
        {
            "id": "intent-catalog-complete",
            "label": "All required Review Workbench UI intents are present",
            "ok": required_intents.issubset(intent_kinds),
        },
        {
            "id": "signals-bound",
            "label": "Qt widget signals dispatch local interaction intents",
            "ok": bool(signal_bindings) and all(binding.get("executes_commands") is False for binding in signal_bindings),
        },
        {
            "id": "toolbar-bound",
            "label": "Toolbar actions are mapped to local or route intents",
            "ok": bool(toolbar_bindings) and all(binding.get("executes_commands") is False for binding in toolbar_bindings),
        },
        {
            "id": "state-reducer-previews",
            "label": "State-changing intents have non-executing reducer previews",
            "ok": bool(state_transitions) and all(transition.get("executes_commands") is False for transition in state_transitions),
        },
        {
            "id": "apply-still-disabled",
            "label": "Apply interaction remains disabled until an explicit reviewed command plan exists",
            "ok": any(
                intent.get("intent_kind") == "toolbar_apply_reviewed_decisions"
                and intent.get("enabled") is False
                and intent.get("executes_commands") is False
                for intent in intent_catalog
            ),
        },
        {
            "id": "headless-safe",
            "label": "Interaction wiring imports no PySide6, opens no window, and executes no commands",
            "ok": all(
                intent.get("requires_pyside6") is False
                and intent.get("opens_window") is False
                and intent.get("executes_commands") is False
                for intent in intent_catalog
            ),
        },
    ]
    failed = [check for check in checks if not check.get("ok")]
    return {
        "ready": not failed,
        "status": "ready" if not failed else "blocked",
        "check_count": len(checks),
        "failed_check_count": len(failed),
        "checks": checks,
        "next_action": (
            "Connect the lazy Qt builder to these intents through callbacks, still without executing media commands."
            if not failed
            else "Fix Review Workbench interaction wiring gaps before connecting live Qt signals."
        ),
    }


def build_review_workbench_interaction_plan(service_bundle: Mapping[str, Any]) -> dict[str, object]:
    """Build the local interaction plan a Qt Review Workbench can wire to signals."""

    intents = _intent_catalog(service_bundle)
    signal_bindings = _signal_bindings(service_bundle)
    toolbar_bindings = _toolbar_bindings(service_bundle)
    state_previews = _state_transition_previews(service_bundle, intents)
    route_previews = _route_previews(service_bundle)
    readiness = _readiness(
        service_bundle=service_bundle,
        intent_catalog=intents,
        signal_bindings=signal_bindings,
        toolbar_bindings=toolbar_bindings,
        state_transitions=state_previews,
    )
    lanes = _lane_ids(service_bundle)
    selected_lane_id = _as_mapping(service_bundle.get("view_model")).get("selected_lane_id")
    return {
        "schema_version": REVIEW_WORKBENCH_INTERACTION_SCHEMA_VERSION,
        "kind": REVIEW_WORKBENCH_INTERACTION_KIND,
        "page_id": "review-workbench",
        "selected_lane_id": selected_lane_id,
        "available_lane_ids": lanes,
        "intent_catalog": intents,
        "signal_bindings": signal_bindings,
        "toolbar_bindings": toolbar_bindings,
        "state_transition_previews": state_previews,
        "route_previews": route_previews,
        "current_state": dict(_state_from_service(service_bundle)),
        "capabilities": {
            "headless_testable": True,
            "requires_pyside6": False,
            "opens_window": False,
            "executes_commands": False,
            "executes_media_operations": False,
            "local_only": True,
            "apply_enabled": False,
        },
        "readiness": readiness,
        "ready": bool(readiness.get("ready")),
        "summary": {
            "intent_count": len(intents),
            "signal_binding_count": len(signal_bindings),
            "toolbar_binding_count": len(toolbar_bindings),
            "state_transition_preview_count": len(state_previews),
            "route_preview_count": len(route_previews),
            "lane_count": len(lanes),
            "selected_lane_id": selected_lane_id,
            "disabled_intent_count": sum(1 for intent in intents if intent.get("enabled") is False),
            "ready": bool(readiness.get("ready")),
            "status": readiness.get("status"),
        },
    }


def write_review_workbench_interaction_plan(out_dir: str | Path, service_bundle: Mapping[str, Any]) -> dict[str, object]:
    root = Path(out_dir)
    root.mkdir(parents=True, exist_ok=True)
    plan = build_review_workbench_interaction_plan(service_bundle)
    plan_path = root / "review_workbench_interaction_plan.json"
    plan_path.write_text(json.dumps(plan, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    preview_path = root / "review_workbench_interaction_state_previews.json"
    preview_path.write_text(
        json.dumps(
            {
                "kind": "ui_review_workbench_interaction_state_previews",
                "page_id": "review-workbench",
                "current_state": plan.get("current_state"),
                "state_transition_previews": plan.get("state_transition_previews"),
                "route_previews": plan.get("route_previews"),
                "executes_commands": False,
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    readme_path = root / "README.txt"
    readme_path.write_text(
        "Review Workbench interaction plan\n"
        "Maps Qt widget signals and toolbar actions to local, non-executing UI intents.\n"
        "This artifact does not import PySide6, open windows, or execute media operations.\n",
        encoding="utf-8",
    )
    return {
        **plan,
        "output_dir": str(root),
        "written_file_count": 3,
        "written_files": [str(plan_path), str(preview_path), str(readme_path)],
    }


__all__ = [
    "REVIEW_WORKBENCH_INTERACTION_KIND",
    "REVIEW_WORKBENCH_INTERACTION_SCHEMA_VERSION",
    "build_review_workbench_interaction_intent",
    "build_review_workbench_interaction_plan",
    "write_review_workbench_interaction_plan",
]
