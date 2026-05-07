from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
import json
from typing import Any

QT_REVIEW_WORKBENCH_WIDGET_SKELETON_SCHEMA_VERSION = "1.0"
QT_REVIEW_WORKBENCH_WIDGET_SKELETON_KIND = "qt_review_workbench_widget_skeleton"

_ROOT_NODE_ID = "review-workbench-root"


def _as_mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _as_list(value: object) -> list[Any]:
    return value if isinstance(value, list) else []


def _as_bool(value: object) -> bool:
    return bool(value)


def _text(value: object, fallback: str = "") -> str:
    if value is None:
        return fallback
    text = str(value).strip()
    return text or fallback


def _object_name(component_id: object) -> str:
    raw = _text(component_id, "review-workbench-component")
    parts = [part for part in raw.replace("_", "-").split("-") if part]
    return "".join(part[:1].upper() + part[1:] for part in parts) or "ReviewWorkbenchComponent"


def _node_for_binding(binding: Mapping[str, Any]) -> dict[str, object]:
    component_id = _text(binding.get("component_id"), "review-workbench-component")
    role = _text(binding.get("role"), "component")
    return {
        "node_id": f"qt-node:{component_id}",
        "parent_node_id": _ROOT_NODE_ID,
        "component_id": component_id,
        "role": role,
        "object_name": _object_name(component_id),
        "qt_widget_class": _text(binding.get("qt_widget_class"), "QWidget"),
        "qt_model_class": _text(binding.get("qt_model_class"), "QObject"),
        "layout_region": _text(binding.get("layout_region"), "center"),
        "child_widget_classes": [str(item) for item in _as_list(binding.get("child_widgets"))],
        "prop_keys": [str(item) for item in _as_list(binding.get("prop_keys"))],
        "sensitive": _as_bool(binding.get("sensitive")),
        "privacy_mode": _text(binding.get("privacy_mode"), "standard_local_view"),
        "requires_pyside6_import": False,
        "opens_window": False,
        "executes_commands": False,
    }


def _model_mount(binding: Mapping[str, Any]) -> dict[str, object]:
    return {
        "mount_id": _text(binding.get("model_binding_id"), f"model-binding:{binding.get('component_id')}"),
        "component_id": binding.get("component_id"),
        "role": binding.get("role"),
        "model_kind": binding.get("model_kind"),
        "qt_model_class": binding.get("qt_model_class"),
        "source_props": [str(item) for item in _as_list(binding.get("source_props"))],
        "mutable_in_widget": bool(binding.get("mutable_in_widget")),
        "executes_commands": False,
    }


def _signal_wiring(binding: Mapping[str, Any]) -> list[dict[str, object]]:
    component_id = _text(binding.get("component_id"), "review-workbench-component")
    signals = [str(item) for item in _as_list(binding.get("signals"))]
    slots = [str(item) for item in _as_list(binding.get("slots"))]
    wires: list[dict[str, object]] = []
    for index, signal in enumerate(signals):
        slot = slots[index] if index < len(slots) else (slots[0] if slots else "noop")
        wires.append(
            {
                "wire_id": f"signal-wire:{component_id}:{index + 1}",
                "component_id": component_id,
                "qt_signal": signal,
                "target_slot": slot,
                "dispatch_strategy": "emit_local_intent",
                "executes_commands": False,
            }
        )
    return wires


def _route_wiring(action_bindings: list[Mapping[str, Any]]) -> list[dict[str, object]]:
    wires: list[dict[str, object]] = []
    for binding in action_bindings:
        action_id = _text(binding.get("action_id"), _text(binding.get("intent_id"), "route"))
        wires.append(
            {
                "route_wire_id": f"route-wire:{action_id}",
                "action_binding_id": binding.get("action_binding_id"),
                "source_component_id": binding.get("source_component_id"),
                "target_page_id": binding.get("target_page_id"),
                "lane_id": binding.get("lane_id"),
                "qt_signal": binding.get("qt_signal"),
                "dispatch": binding.get("dispatch"),
                "enabled": bool(binding.get("enabled")),
                "executes_immediately": False,
                "executes_commands": False,
            }
        )
    return wires


def _root_node(root_layout: Mapping[str, Any], nodes: list[Mapping[str, Any]]) -> dict[str, object]:
    return {
        "node_id": _ROOT_NODE_ID,
        "parent_node_id": None,
        "component_id": "review-workbench",
        "role": "page_root",
        "object_name": "ReviewWorkbenchPage",
        "qt_widget_class": _text(root_layout.get("root_widget_class"), "QWidget"),
        "root_layout_class": _text(root_layout.get("root_layout_class"), "QVBoxLayout"),
        "content_splitter_class": _text(root_layout.get("content_splitter_class"), "QSplitter"),
        "layout_regions": _as_mapping(root_layout.get("regions")),
        "child_node_ids": [str(node.get("node_id")) for node in nodes],
        "requires_pyside6_import": False,
        "opens_window": False,
        "executes_commands": False,
    }


def _readiness(
    *,
    widget_binding_plan: Mapping[str, Any],
    nodes: list[Mapping[str, Any]],
    model_mounts: list[Mapping[str, Any]],
    signal_wiring: list[Mapping[str, Any]],
    route_wiring: list[Mapping[str, Any]],
) -> dict[str, object]:
    roles = {str(node.get("role")) for node in nodes}
    required_roles = {"toolbar", "filter_bar", "review_lane_table", "lane_detail"}
    checks = [
        {
            "id": "binding-plan-ready",
            "label": "The widget binding plan is ready before skeleton generation",
            "ok": bool(widget_binding_plan.get("ready")),
        },
        {
            "id": "required-nodes",
            "label": "The skeleton contains all required Review Workbench widget roles",
            "ok": required_roles.issubset(roles),
        },
        {
            "id": "model-mounts",
            "label": "Every widget node has a model mount descriptor",
            "ok": len(model_mounts) >= len(nodes) and len(nodes) > 0,
        },
        {
            "id": "signal-wiring",
            "label": "Widget signals are mapped to local intent slots",
            "ok": bool(signal_wiring),
        },
        {
            "id": "route-wiring-safe",
            "label": "Route wiring is deferred and never executes commands immediately",
            "ok": bool(route_wiring) and all(
                wire.get("executes_commands") is False and wire.get("executes_immediately") is False for wire in route_wiring
            ),
        },
        {
            "id": "headless-safe",
            "label": "The skeleton can be built without PySide6, windows, or media operations",
            "ok": all(
                node.get("requires_pyside6_import") is False
                and node.get("opens_window") is False
                and node.get("executes_commands") is False
                for node in nodes
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
            "Mount this skeleton through the lazy PySide6 Qt builder and keep command execution behind explicit command plans."
            if not failed
            else "Fix the skeleton gaps before wiring real Review Workbench widgets."
        ),
    }


def build_qt_review_workbench_widget_skeleton(widget_binding_plan: Mapping[str, Any]) -> dict[str, object]:
    """Build a concrete widget skeleton from the descriptor-only binding plan.

    This remains pure data: it imports no PySide6, opens no window, and executes
    no media operations. The runtime Qt builder can consume the returned nodes
    when PySide6 is explicitly available.
    """

    widget_bindings = [item for item in _as_list(widget_binding_plan.get("widget_bindings")) if isinstance(item, Mapping)]
    model_bindings = [item for item in _as_list(widget_binding_plan.get("model_bindings")) if isinstance(item, Mapping)]
    action_bindings = [item for item in _as_list(widget_binding_plan.get("action_bindings")) if isinstance(item, Mapping)]
    nodes = [_node_for_binding(binding) for binding in widget_bindings]
    model_mounts = [_model_mount(binding) for binding in model_bindings]
    signal_wires = [wire for binding in widget_bindings for wire in _signal_wiring(binding)]
    route_wires = _route_wiring(action_bindings)
    root_layout = _as_mapping(widget_binding_plan.get("root_layout"))
    root_node = _root_node(root_layout, nodes)
    readiness = _readiness(
        widget_binding_plan=widget_binding_plan,
        nodes=nodes,
        model_mounts=model_mounts,
        signal_wiring=signal_wires,
        route_wiring=route_wires,
    )
    sensitive_nodes = [node for node in nodes if node.get("sensitive")]
    return {
        "schema_version": QT_REVIEW_WORKBENCH_WIDGET_SKELETON_SCHEMA_VERSION,
        "kind": QT_REVIEW_WORKBENCH_WIDGET_SKELETON_KIND,
        "page_id": "review-workbench",
        "source_binding_kind": widget_binding_plan.get("kind"),
        "root_node": root_node,
        "nodes": nodes,
        "model_mounts": model_mounts,
        "signal_wiring": signal_wires,
        "route_wiring": route_wires,
        "builder_contract": {
            "module": "media_manager.gui_review_workbench_qt",
            "builder_function": "build_review_workbench_page_widget",
            "requires_qtwidgets_argument": True,
            "loads_pyside6_at_import_time": False,
            "opens_window": False,
            "executes_commands": False,
        },
        "capabilities": {
            "headless_testable": True,
            "requires_pyside6": False,
            "loads_pyside6_at_import_time": False,
            "opens_window": False,
            "executes_commands": False,
            "local_only": True,
            "apply_enabled": False,
        },
        "readiness": readiness,
        "ready": bool(readiness.get("ready")),
        "summary": {
            "node_count": len(nodes),
            "model_mount_count": len(model_mounts),
            "signal_wire_count": len(signal_wires),
            "route_wire_count": len(route_wires),
            "sensitive_node_count": len(sensitive_nodes),
            "ready": bool(readiness.get("ready")),
            "status": readiness.get("status"),
        },
    }


def write_qt_review_workbench_widget_skeleton(out_dir: str | Path, widget_binding_plan: Mapping[str, Any]) -> dict[str, object]:
    root = Path(out_dir)
    root.mkdir(parents=True, exist_ok=True)
    skeleton = build_qt_review_workbench_widget_skeleton(widget_binding_plan)
    skeleton_path = root / "review_workbench_qt_widget_skeleton.json"
    skeleton_path.write_text(json.dumps(skeleton, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    readme_path = root / "README.txt"
    readme_path.write_text(
        "Review Workbench Qt widget skeleton\n"
        "Pure-data skeleton consumed by the lazy PySide6 Review Workbench builder.\n"
        "This artifact does not import PySide6, open windows, or execute media operations.\n",
        encoding="utf-8",
    )
    return {
        **skeleton,
        "output_dir": str(root),
        "written_file_count": 2,
        "written_files": [str(skeleton_path), str(readme_path)],
    }


__all__ = [
    "QT_REVIEW_WORKBENCH_WIDGET_SKELETON_KIND",
    "QT_REVIEW_WORKBENCH_WIDGET_SKELETON_SCHEMA_VERSION",
    "build_qt_review_workbench_widget_skeleton",
    "write_qt_review_workbench_widget_skeleton",
]
