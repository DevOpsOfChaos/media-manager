from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
import json
from typing import Any

REVIEW_WORKBENCH_CALLBACK_MOUNT_SCHEMA_VERSION = "1.0"
REVIEW_WORKBENCH_CALLBACK_MOUNT_KIND = "ui_review_workbench_callback_mount_plan"


def _as_mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _as_list(value: object) -> list[Any]:
    return value if isinstance(value, list) else []


def _text(value: object, fallback: str = "") -> str:
    if value is None:
        return fallback
    text = str(value).strip()
    return text or fallback


def _intent_by_kind(interaction_plan: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    result: dict[str, Mapping[str, Any]] = {}
    for item in _as_list(interaction_plan.get("intent_catalog")):
        intent = _as_mapping(item)
        intent_kind = _text(intent.get("intent_kind"))
        if intent_kind:
            result[intent_kind] = intent
    return result


def _available_lane_ids(service_bundle: Mapping[str, Any]) -> list[str]:
    interaction_plan = _as_mapping(service_bundle.get("interaction_plan"))
    lane_ids = interaction_plan.get("available_lane_ids")
    if isinstance(lane_ids, list):
        return [str(item) for item in lane_ids if str(item or "").strip()]
    view_model = _as_mapping(service_bundle.get("view_model"))
    raw_lane_ids = view_model.get("available_lane_ids")
    if isinstance(raw_lane_ids, list):
        return [str(item) for item in raw_lane_ids if str(item or "").strip()]
    return []


def _mount(
    *,
    mount_id: str,
    component_id: str,
    object_name: str,
    qt_signal: str,
    intent_kind: str,
    payload_source: str,
    payload_field: str | None = None,
    value_transform: str = "identity",
    enabled: bool = True,
    reason: str | None = None,
) -> dict[str, object]:
    return {
        "mount_id": mount_id,
        "component_id": component_id,
        "object_name": object_name,
        "qt_signal": qt_signal,
        "intent_kind": intent_kind,
        "callback_name": f"dispatch_{intent_kind}",
        "payload_source": payload_source,
        "payload_field": payload_field,
        "value_transform": value_transform,
        "enabled": bool(enabled),
        "disabled_reason": reason if not enabled else None,
        "dispatch_strategy": "local_intent_dispatcher",
        "updates_state_only": intent_kind in {"filter_query_changed", "filter_status_changed", "sort_mode_changed", "lane_selected"},
        "route_deferred": intent_kind in {"table_row_activated", "toolbar_open_selected_lane"},
        "requires_explicit_user_confirmation": intent_kind == "toolbar_apply_reviewed_decisions",
        "executes_immediately": False,
        "executes_commands": False,
        "opens_window": False,
        "requires_pyside6": False,
    }


def _callback_mounts(service_bundle: Mapping[str, Any]) -> list[dict[str, object]]:
    interaction_plan = _as_mapping(service_bundle.get("interaction_plan"))
    intents = _intent_by_kind(interaction_plan)
    lane_ids = _available_lane_ids(service_bundle)
    selected_lane_id = _text(interaction_plan.get("selected_lane_id")) or (lane_ids[0] if lane_ids else "")
    return [
        _mount(
            mount_id="callback:query:textChanged",
            component_id="review-workbench-filter-bar",
            object_name="ReviewWorkbenchQuery",
            qt_signal="QLineEdit.textChanged",
            intent_kind="filter_query_changed",
            payload_source="signal_arg_0",
            payload_field="query",
            enabled="filter_query_changed" in intents,
        ),
        _mount(
            mount_id="callback:status:currentTextChanged",
            component_id="review-workbench-filter-bar",
            object_name="ReviewWorkbenchStatusFilter",
            qt_signal="QComboBox.currentTextChanged",
            intent_kind="filter_status_changed",
            payload_source="signal_arg_0",
            payload_field="status",
            enabled="filter_status_changed" in intents,
        ),
        _mount(
            mount_id="callback:sort:currentTextChanged",
            component_id="review-workbench-filter-bar",
            object_name="ReviewWorkbenchSortMode",
            qt_signal="QComboBox.currentTextChanged",
            intent_kind="sort_mode_changed",
            payload_source="signal_arg_0",
            payload_field="sort_mode",
            enabled="sort_mode_changed" in intents,
        ),
        _mount(
            mount_id="callback:table:itemSelectionChanged",
            component_id="review-workbench-lane-table",
            object_name="ReviewWorkbenchLaneTable",
            qt_signal="QTableWidget.itemSelectionChanged",
            intent_kind="lane_selected",
            payload_source="current_table_row",
            payload_field="lane_id",
            value_transform="row_to_lane_id",
            enabled="lane_selected" in intents and bool(lane_ids),
            reason=None if lane_ids else "No review lanes are available.",
        ),
        _mount(
            mount_id="callback:table:cellDoubleClicked",
            component_id="review-workbench-lane-table",
            object_name="ReviewWorkbenchLaneTable",
            qt_signal="QTableWidget.cellDoubleClicked",
            intent_kind="table_row_activated",
            payload_source="signal_arg_0",
            payload_field="lane_id",
            value_transform="row_to_lane_id",
            enabled="table_row_activated" in intents and bool(lane_ids),
            reason=None if lane_ids else "No review lanes are available.",
        ),
        _mount(
            mount_id="callback:detail:primary.clicked",
            component_id="review-workbench-lane-detail",
            object_name="ReviewWorkbenchLaneDetailPrimaryAction",
            qt_signal="QPushButton.clicked",
            intent_kind="toolbar_open_selected_lane",
            payload_source="selected_lane_id",
            payload_field="lane_id",
            value_transform="selected_lane_id",
            enabled="toolbar_open_selected_lane" in intents and bool(selected_lane_id),
            reason=None if selected_lane_id else "Select a lane before routing.",
        ),
    ]


def _toolbar_callback_mounts(service_bundle: Mapping[str, Any]) -> list[dict[str, object]]:
    interaction_plan = _as_mapping(service_bundle.get("interaction_plan"))
    result: list[dict[str, object]] = []
    for binding in _as_list(interaction_plan.get("toolbar_bindings")):
        toolbar_binding = _as_mapping(binding)
        action_id = _text(toolbar_binding.get("action_id"), "action")
        intent_kind = _text(toolbar_binding.get("intent_kind"), "noop")
        result.append(
            _mount(
                mount_id=f"callback:toolbar:{action_id}.triggered",
                component_id="review-workbench-toolbar",
                object_name=f"ReviewWorkbenchAction:{action_id}",
                qt_signal="QAction.triggered",
                intent_kind=intent_kind,
                payload_source="action_metadata",
                payload_field="lane_id",
                value_transform="action_metadata",
                enabled=bool(toolbar_binding.get("enabled")),
                reason=None if toolbar_binding.get("enabled") else "Toolbar action is disabled by the action plan.",
            )
        )
    return result


def _readiness(
    *,
    service_bundle: Mapping[str, Any],
    widget_mounts: list[Mapping[str, Any]],
    toolbar_mounts: list[Mapping[str, Any]],
) -> dict[str, object]:
    enabled_widget_mounts = [mount for mount in widget_mounts if mount.get("enabled") is True]
    all_mounts = [*widget_mounts, *toolbar_mounts]
    widget_intents = {str(mount.get("intent_kind")) for mount in widget_mounts}
    required_widget_intents = {
        "filter_query_changed",
        "filter_status_changed",
        "sort_mode_changed",
        "lane_selected",
        "table_row_activated",
        "toolbar_open_selected_lane",
    }
    checks = [
        {
            "id": "service-ready",
            "label": "Review Workbench service and interaction plan are ready before callback mounting",
            "ok": bool(_as_mapping(service_bundle.get("readiness")).get("ready"))
            or bool(_as_mapping(_as_mapping(service_bundle.get("interaction_plan")).get("readiness")).get("ready")),
        },
        {
            "id": "widget-callbacks-covered",
            "label": "Filter, sort, table selection, table activation and detail callbacks are described",
            "ok": required_widget_intents.issubset(widget_intents),
        },
        {
            "id": "state-callbacks-enabled",
            "label": "State-changing widget callbacks are enabled when lanes exist",
            "ok": bool(enabled_widget_mounts)
            and all(
                any(mount.get("intent_kind") == intent_kind and mount.get("enabled") is True for mount in widget_mounts)
                for intent_kind in {"filter_query_changed", "filter_status_changed", "sort_mode_changed"}
            ),
        },
        {
            "id": "toolbar-callbacks-described",
            "label": "Toolbar actions have callback mount descriptors",
            "ok": len(toolbar_mounts) >= 4,
        },
        {
            "id": "apply-remains-disabled",
            "label": "Apply callback remains disabled and confirmation gated",
            "ok": any(
                mount.get("intent_kind") == "toolbar_apply_reviewed_decisions"
                and mount.get("enabled") is False
                and mount.get("requires_explicit_user_confirmation") is True
                for mount in toolbar_mounts
            ),
        },
        {
            "id": "headless-safe",
            "label": "Callback mounts import no PySide6, open no window, and execute no commands",
            "ok": all(
                mount.get("requires_pyside6") is False
                and mount.get("opens_window") is False
                and mount.get("executes_commands") is False
                and mount.get("executes_immediately") is False
                for mount in all_mounts
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
            "Mount these callbacks in the lazy Qt builder and dispatch only local UI intents."
            if not failed
            else "Fix callback mount gaps before wiring live Qt signals."
        ),
    }


def build_review_workbench_callback_mount_plan(service_bundle: Mapping[str, Any]) -> dict[str, object]:
    """Build the descriptor contract used by the lazy Qt builder to connect signals.

    The plan describes callbacks; it does not import Qt, open windows, execute
    media operations, or apply decisions.
    """

    widget_mounts = _callback_mounts(service_bundle)
    toolbar_mounts = _toolbar_callback_mounts(service_bundle)
    readiness = _readiness(service_bundle=service_bundle, widget_mounts=widget_mounts, toolbar_mounts=toolbar_mounts)
    all_mounts = [*widget_mounts, *toolbar_mounts]
    return {
        "schema_version": REVIEW_WORKBENCH_CALLBACK_MOUNT_SCHEMA_VERSION,
        "kind": REVIEW_WORKBENCH_CALLBACK_MOUNT_KIND,
        "page_id": "review-workbench",
        "widget_callback_mounts": widget_mounts,
        "toolbar_callback_mounts": toolbar_mounts,
        "callback_mounts": all_mounts,
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
            "widget_callback_mount_count": len(widget_mounts),
            "toolbar_callback_mount_count": len(toolbar_mounts),
            "callback_mount_count": len(all_mounts),
            "enabled_callback_mount_count": sum(1 for mount in all_mounts if mount.get("enabled") is True),
            "disabled_callback_mount_count": sum(1 for mount in all_mounts if mount.get("enabled") is False),
            "route_deferred_callback_count": sum(1 for mount in all_mounts if mount.get("route_deferred") is True),
            "state_only_callback_count": sum(1 for mount in all_mounts if mount.get("updates_state_only") is True),
            "ready": bool(readiness.get("ready")),
            "status": readiness.get("status"),
        },
    }


def write_review_workbench_callback_mount_plan(out_dir: str | Path, service_bundle: Mapping[str, Any]) -> dict[str, object]:
    root = Path(out_dir)
    root.mkdir(parents=True, exist_ok=True)
    plan = build_review_workbench_callback_mount_plan(service_bundle)
    plan_path = root / "review_workbench_callback_mount_plan.json"
    plan_path.write_text(json.dumps(plan, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    readme_path = root / "README.txt"
    readme_path.write_text(
        "Review Workbench callback mount plan\n"
        "Maps concrete Qt signals to local, non-executing Review Workbench intent dispatch callbacks.\n"
        "The artifact is descriptor-only: no PySide6 import, no window, no media operation, no apply.\n",
        encoding="utf-8",
    )
    return {
        **plan,
        "output_dir": str(root),
        "written_file_count": 2,
        "written_files": [str(plan_path), str(readme_path)],
    }


__all__ = [
    "REVIEW_WORKBENCH_CALLBACK_MOUNT_KIND",
    "REVIEW_WORKBENCH_CALLBACK_MOUNT_SCHEMA_VERSION",
    "build_review_workbench_callback_mount_plan",
    "write_review_workbench_callback_mount_plan",
]
