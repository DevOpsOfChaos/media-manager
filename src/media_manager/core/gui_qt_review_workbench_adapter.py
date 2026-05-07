from __future__ import annotations

from collections.abc import Mapping
from typing import Any

QT_REVIEW_WORKBENCH_ADAPTER_SCHEMA_VERSION = "1.0"
QT_REVIEW_WORKBENCH_ADAPTER_KIND = "qt_review_workbench_adapter_package"


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


def _component(component_id: str, component_type: str, *, role: str, props: Mapping[str, Any], sensitive: bool = False) -> dict[str, object]:
    return {
        "component_id": component_id,
        "component_type": component_type,
        "role": role,
        "props": dict(props),
        "sensitive": sensitive,
        "requires_pyside6": False,
        "opens_window": False,
        "executes_commands": False,
    }


def _toolbar_component(view_model: Mapping[str, Any], action_plan: Mapping[str, Any]) -> dict[str, object]:
    actions = [dict(action) for action in _as_list(action_plan.get("actions")) if isinstance(action, Mapping)]
    return _component(
        "review-workbench-toolbar",
        "ReviewWorkbenchToolbar",
        role="toolbar",
        props={
            "title": view_model.get("title") or "Review workbench",
            "selected_lane_id": view_model.get("selected_lane_id"),
            "actions": actions,
            "enabled_action_count": action_plan.get("enabled_action_count", 0),
        },
    )


def _table_component(table_model: Mapping[str, Any]) -> dict[str, object]:
    rows = [dict(row) for row in _as_list(table_model.get("rows")) if isinstance(row, Mapping)]
    return _component(
        "review-workbench-table",
        "ReviewWorkbenchTable",
        role="review_lane_table",
        props={
            "columns": _as_list(table_model.get("columns")),
            "rows": rows,
            "pagination": dict(_as_mapping(table_model.get("pagination"))),
            "selected_lane_id": table_model.get("selected_lane_id"),
        },
    )


def _detail_component(view_model: Mapping[str, Any]) -> dict[str, object]:
    detail = _as_mapping(view_model.get("selected_lane_detail"))
    lane_id = str(detail.get("lane_id") or view_model.get("selected_lane_id") or "")
    return _component(
        "review-workbench-detail",
        "ReviewWorkbenchLaneDetail",
        role="lane_detail",
        props={
            "lane_id": lane_id or None,
            "headline": detail.get("headline") or "No lane selected",
            "description": detail.get("description") or "",
            "recommended_next_step": detail.get("recommended_next_step"),
            "primary_action": detail.get("primary_action"),
            "has_attention": detail.get("has_attention", False),
        },
        sensitive=lane_id == "people-review",
    )


def _filter_component(view_model: Mapping[str, Any]) -> dict[str, object]:
    lane_filter = _as_mapping(view_model.get("lane_filter"))
    lane_sort = _as_mapping(view_model.get("lane_sort"))
    return _component(
        "review-workbench-filter-bar",
        "ReviewWorkbenchFilterBar",
        role="filter_bar",
        props={
            "status": lane_filter.get("status") or "all",
            "query": lane_filter.get("query") or "",
            "available_statuses": _as_list(lane_filter.get("available_statuses")),
            "sort_mode": lane_sort.get("mode") or "attention_first",
            "available_sort_modes": _as_list(lane_sort.get("available_modes")),
        },
    )


def _route_intents(view_model: Mapping[str, Any], action_plan: Mapping[str, Any]) -> list[dict[str, object]]:
    intents: list[dict[str, object]] = []
    for action in _as_list(action_plan.get("actions")):
        if not isinstance(action, Mapping):
            continue
        page_id = str(action.get("page_id") or "")
        if not page_id:
            continue
        intents.append(
            {
                "intent_id": f"route:{action.get('id')}",
                "action_id": action.get("id"),
                "target_page_id": page_id,
                "lane_id": action.get("lane_id") or view_model.get("selected_lane_id"),
                "enabled": bool(action.get("enabled")),
                "executes_immediately": False,
                "executes_commands": False,
            }
        )
    return intents


def _readiness(*, components: list[Mapping[str, Any]], route_intents: list[Mapping[str, Any]], action_plan: Mapping[str, Any]) -> dict[str, object]:
    checks = [
        {"id": "components", "label": "Adapter exposes Qt component descriptors", "ok": bool(components)},
        {
            "id": "safe-components",
            "label": "Components do not require PySide6, windows, or command execution",
            "ok": all(
                component.get("requires_pyside6") is False
                and component.get("opens_window") is False
                and component.get("executes_commands") is False
                for component in components
            ),
        },
        {
            "id": "route-intents",
            "label": "Enabled navigation is expressed as route intents instead of command execution",
            "ok": bool(route_intents),
        },
        {
            "id": "apply-blocked",
            "label": "Apply remains disabled until a reviewed command plan exists",
            "ok": _as_mapping(action_plan.get("capabilities")).get("apply_enabled") is False,
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
            "Bind these descriptors to real Qt widgets while keeping command execution behind explicit plans."
            if not failed
            else "Fix the failing adapter checks before adding real Qt widgets."
        ),
    }


def build_qt_review_workbench_adapter_package(
    *,
    view_model: Mapping[str, Any],
    table_model: Mapping[str, Any],
    action_plan: Mapping[str, Any],
    controller_state: Mapping[str, Any],
    qt_workbench: Mapping[str, Any],
) -> dict[str, object]:
    """Create a Qt-facing adapter package without importing Qt.

    This is the bridge between the headless Review Workbench service and a real
    desktop implementation. It deliberately contains component descriptors,
    route intents, and safety metadata rather than QWidget instances.
    """

    components = [
        _toolbar_component(view_model, action_plan),
        _filter_component(view_model),
        _table_component(table_model),
        _detail_component(view_model),
    ]
    route_intents = _route_intents(view_model, action_plan)
    readiness = _readiness(components=components, route_intents=route_intents, action_plan=action_plan)
    controller_inner_state = _as_mapping(controller_state.get("state"))
    guard = _as_mapping(qt_workbench.get("guard"))
    summary = {
        "component_count": len(components),
        "route_intent_count": len(route_intents),
        "row_count": _as_mapping(table_model.get("summary")).get("row_count", 0),
        "selected_lane_id": view_model.get("selected_lane_id"),
        "attention_count": _as_mapping(view_model.get("summary")).get("attention_count", 0),
        "guard_problem_count": guard.get("problem_count", 0),
        "ready": readiness.get("ready"),
    }
    return {
        "schema_version": QT_REVIEW_WORKBENCH_ADAPTER_SCHEMA_VERSION,
        "kind": QT_REVIEW_WORKBENCH_ADAPTER_KIND,
        "page_id": "review-workbench",
        "components": components,
        "route_intents": route_intents,
        "controller_state": dict(controller_inner_state),
        "workspace_guard": dict(guard),
        "readiness": readiness,
        "ready": bool(readiness.get("ready")),
        "summary": summary,
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
    "QT_REVIEW_WORKBENCH_ADAPTER_KIND",
    "QT_REVIEW_WORKBENCH_ADAPTER_SCHEMA_VERSION",
    "build_qt_review_workbench_adapter_package",
]
