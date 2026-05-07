from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
import json
from typing import Any

QT_REVIEW_WORKBENCH_WIDGET_BINDING_SCHEMA_VERSION = "1.0"
QT_REVIEW_WORKBENCH_WIDGET_BINDING_KIND = "qt_review_workbench_widget_binding_plan"

_ROLE_BINDING_SPECS: dict[str, dict[str, object]] = {
    "toolbar": {
        "qt_widget_class": "QToolBar",
        "qt_model_class": "QAction",
        "layout_region": "top",
        "required_props": ["title", "actions"],
        "signals": ["QAction.triggered"],
        "slots": ["route_intent_requested"],
    },
    "filter_bar": {
        "qt_widget_class": "QWidget",
        "qt_model_class": "FilterBarState",
        "layout_region": "top",
        "child_widgets": ["QLineEdit", "QComboBox"],
        "required_props": ["query", "status", "sort_mode"],
        "signals": ["QLineEdit.textChanged", "QComboBox.currentTextChanged", "QComboBox.currentTextChanged"],
        "slots": ["filter_query_changed", "filter_status_changed", "sort_changed"],
    },
    "review_lane_table": {
        "qt_widget_class": "QTableView",
        "qt_model_class": "QAbstractTableModel",
        "layout_region": "center",
        "required_props": ["columns", "rows", "pagination"],
        "signals": ["QItemSelectionModel.selectionChanged", "QTableView.doubleClicked", "QAbstractItemModel.dataChanged"],
        "slots": ["selected_lane_changed", "row_activated", "refresh_requested"],
    },
    "lane_detail": {
        "qt_widget_class": "QWidget",
        "qt_model_class": "LaneDetailState",
        "layout_region": "right",
        "child_widgets": ["QLabel", "QTextEdit", "QPushButton"],
        "required_props": ["lane_id", "headline", "description"],
        "signals": ["QPushButton.clicked"],
        "slots": ["primary_lane_action_requested"],
    },
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


def _normalize_component_id(value: object) -> str:
    return str(value or "review-workbench-component").strip() or "review-workbench-component"


def _component_binding(component: Mapping[str, Any]) -> dict[str, object]:
    role = str(component.get("role") or "component")
    spec = _ROLE_BINDING_SPECS.get(role, {})
    props = _as_mapping(component.get("props"))
    required_props = [str(item) for item in _as_list(spec.get("required_props"))]
    missing_props = [name for name in required_props if name not in props]
    component_id = _normalize_component_id(component.get("component_id"))
    sensitive = bool(component.get("sensitive"))
    return {
        "binding_id": f"widget-binding:{component_id}",
        "component_id": component_id,
        "component_type": str(component.get("component_type") or "ReviewWorkbenchComponent"),
        "role": role,
        "layout_region": str(spec.get("layout_region") or "center"),
        "qt_widget_class": str(spec.get("qt_widget_class") or "QWidget"),
        "qt_model_class": str(spec.get("qt_model_class") or "QObject"),
        "child_widgets": [str(item) for item in _as_list(spec.get("child_widgets"))],
        "required_props": required_props,
        "missing_props": missing_props,
        "prop_keys": sorted(str(key) for key in props.keys()),
        "signals": [str(item) for item in _as_list(spec.get("signals"))],
        "slots": [str(item) for item in _as_list(spec.get("slots"))],
        "sensitive": sensitive,
        "privacy_mode": "local_redacted_preview" if sensitive else "standard_local_view",
        "requires_pyside6_import": False,
        "opens_window": False,
        "executes_commands": False,
        "ready": not missing_props and role in _ROLE_BINDING_SPECS,
    }


def _model_binding(binding: Mapping[str, Any]) -> dict[str, object]:
    role = str(binding.get("role") or "component")
    model_kind = {
        "toolbar": "action_collection_model",
        "filter_bar": "filter_state_model",
        "review_lane_table": "review_lane_table_model",
        "lane_detail": "lane_detail_state_model",
    }.get(role, "generic_component_model")
    return {
        "model_binding_id": f"model-binding:{binding.get('component_id')}",
        "component_id": binding.get("component_id"),
        "role": role,
        "model_kind": model_kind,
        "qt_model_class": binding.get("qt_model_class"),
        "source_props": list(binding.get("prop_keys", [])) if isinstance(binding.get("prop_keys"), list) else [],
        "mutable_in_widget": role in {"filter_bar", "review_lane_table"},
        "executes_commands": False,
    }


def _action_bindings(adapter_package: Mapping[str, Any]) -> list[dict[str, object]]:
    actions: list[dict[str, object]] = []
    for intent in _as_list(adapter_package.get("route_intents")):
        if not isinstance(intent, Mapping):
            continue
        action_id = str(intent.get("action_id") or intent.get("intent_id") or "route")
        actions.append(
            {
                "action_binding_id": f"action-binding:{action_id}",
                "intent_id": intent.get("intent_id"),
                "action_id": action_id,
                "source_component_id": "review-workbench-toolbar",
                "target_page_id": intent.get("target_page_id"),
                "lane_id": intent.get("lane_id"),
                "enabled": bool(intent.get("enabled")),
                "qt_signal": "QAction.triggered",
                "dispatch": "route_intent_requested",
                "executes_immediately": False,
                "executes_commands": False,
            }
        )
    return actions


def _root_layout(widget_bindings: list[Mapping[str, Any]]) -> dict[str, object]:
    regions: dict[str, list[str]] = {"top": [], "center": [], "right": [], "bottom": []}
    for binding in widget_bindings:
        region = str(binding.get("layout_region") or "center")
        regions.setdefault(region, []).append(str(binding.get("component_id")))
    return {
        "root_widget_class": "QWidget",
        "root_layout_class": "QVBoxLayout",
        "content_splitter_class": "QSplitter",
        "splitter_orientation": "horizontal",
        "regions": regions,
        "composition_order": ["top", "center", "right", "bottom"],
        "opens_window": False,
        "requires_pyside6_import": False,
    }


def _readiness(*, adapter_package: Mapping[str, Any], widget_bindings: list[Mapping[str, Any]], action_bindings: list[Mapping[str, Any]]) -> dict[str, object]:
    component_ids = [str(binding.get("component_id")) for binding in widget_bindings]
    covered_roles = {str(binding.get("role")) for binding in widget_bindings}
    required_roles = set(_ROLE_BINDING_SPECS)
    checks = [
        {
            "id": "adapter-ready",
            "label": "Review Workbench adapter package is ready",
            "ok": bool(adapter_package.get("ready")),
        },
        {
            "id": "roles-covered",
            "label": "All Review Workbench component roles have Qt widget bindings",
            "ok": required_roles.issubset(covered_roles),
        },
        {
            "id": "unique-components",
            "label": "Each Qt component binding has a unique component id",
            "ok": len(component_ids) == len(set(component_ids)),
        },
        {
            "id": "required-props",
            "label": "All Qt widget bindings have the required adapter props",
            "ok": all(not binding.get("missing_props") and binding.get("ready") is True for binding in widget_bindings),
        },
        {
            "id": "table-model-binding",
            "label": "Review lane table is bound to a QAbstractTableModel descriptor",
            "ok": any(binding.get("role") == "review_lane_table" and binding.get("qt_model_class") == "QAbstractTableModel" for binding in widget_bindings),
        },
        {
            "id": "route-actions-safe",
            "label": "Route actions dispatch intents and do not execute commands",
            "ok": bool(action_bindings) and all(action.get("executes_commands") is False and action.get("executes_immediately") is False for action in action_bindings),
        },
        {
            "id": "headless-safe",
            "label": "Widget binding plan requires no PySide6 import, opens no window, and executes no commands",
            "ok": all(
                binding.get("requires_pyside6_import") is False
                and binding.get("opens_window") is False
                and binding.get("executes_commands") is False
                for binding in widget_bindings
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
            "Implement real Qt widgets from this binding plan and keep command execution behind explicit command plans."
            if not failed
            else "Fix the Review Workbench widget binding gaps before creating real Qt widgets."
        ),
    }


def build_qt_review_workbench_widget_binding_plan(adapter_package: Mapping[str, Any]) -> dict[str, object]:
    """Map Review Workbench adapter components to concrete Qt widget roles.

    The result is intentionally a descriptor-only plan. It names Qt classes,
    model roles, signals, slots, and routing semantics without importing PySide6,
    opening a window, or executing media operations.
    """

    components = [item for item in _as_list(adapter_package.get("components")) if isinstance(item, Mapping)]
    widget_bindings = [_component_binding(component) for component in components]
    model_bindings = [_model_binding(binding) for binding in widget_bindings]
    action_bindings = _action_bindings(adapter_package)
    root_layout = _root_layout(widget_bindings)
    readiness = _readiness(adapter_package=adapter_package, widget_bindings=widget_bindings, action_bindings=action_bindings)
    sensitive_count = sum(1 for binding in widget_bindings if binding.get("sensitive"))
    return {
        "schema_version": QT_REVIEW_WORKBENCH_WIDGET_BINDING_SCHEMA_VERSION,
        "kind": QT_REVIEW_WORKBENCH_WIDGET_BINDING_KIND,
        "page_id": "review-workbench",
        "adapter_kind": adapter_package.get("kind"),
        "root_layout": root_layout,
        "widget_bindings": widget_bindings,
        "model_bindings": model_bindings,
        "action_bindings": action_bindings,
        "capabilities": {
            "headless_testable": True,
            "requires_pyside6": False,
            "opens_window": False,
            "executes_commands": False,
            "local_only": True,
            "apply_enabled": False,
            "descriptor_only": True,
        },
        "readiness": readiness,
        "ready": bool(readiness.get("ready")),
        "summary": {
            "widget_binding_count": len(widget_bindings),
            "model_binding_count": len(model_bindings),
            "action_binding_count": len(action_bindings),
            "sensitive_widget_count": sensitive_count,
            "table_binding_count": sum(1 for binding in widget_bindings if binding.get("role") == "review_lane_table"),
            "enabled_action_binding_count": sum(1 for binding in action_bindings if binding.get("enabled")),
            "route_intent_count": _as_int(_as_mapping(adapter_package.get("summary")).get("route_intent_count")),
            "ready": bool(readiness.get("ready")),
            "status": readiness.get("status"),
        },
    }


def write_qt_review_workbench_widget_binding_plan(out_dir: str | Path, adapter_package: Mapping[str, Any]) -> dict[str, object]:
    root = Path(out_dir)
    root.mkdir(parents=True, exist_ok=True)
    plan = build_qt_review_workbench_widget_binding_plan(adapter_package)
    plan_path = root / "review_workbench_qt_widget_binding_plan.json"
    plan_path.write_text(json.dumps(plan, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    readme_path = root / "README.txt"
    readme_path.write_text(
        "Review Workbench Qt widget binding plan\n"
        "Descriptor-only bridge from adapter components to concrete Qt widget roles.\n"
        "It does not import PySide6, does not open a window, and does not execute media operations.\n",
        encoding="utf-8",
    )
    return {
        **plan,
        "output_dir": str(root),
        "written_file_count": 2,
        "written_files": [str(plan_path), str(readme_path)],
    }


__all__ = [
    "QT_REVIEW_WORKBENCH_WIDGET_BINDING_KIND",
    "QT_REVIEW_WORKBENCH_WIDGET_BINDING_SCHEMA_VERSION",
    "build_qt_review_workbench_widget_binding_plan",
    "write_qt_review_workbench_widget_binding_plan",
]
