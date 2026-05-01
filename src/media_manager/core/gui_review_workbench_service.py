from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

from .gui_review_workbench_action_plan import build_review_workbench_action_plan
from .gui_review_workbench_controller import build_review_workbench_view_state
from .gui_qt_review_workbench import build_qt_review_workbench
from .gui_qt_review_workbench_adapter import build_qt_review_workbench_adapter_package
from .gui_qt_review_workbench_widget_bindings import build_qt_review_workbench_widget_binding_plan
from .gui_qt_review_workbench_widget_skeleton import build_qt_review_workbench_widget_skeleton
from .gui_review_workbench_interactions import build_review_workbench_interaction_plan
from .gui_review_workbench_callback_mounts import build_review_workbench_callback_mount_plan
from .gui_review_workbench_apply_preview import build_review_workbench_apply_preview
from .gui_review_workbench_confirmation_dialog import build_review_workbench_confirmation_dialog_model
from .gui_review_workbench_apply_executor_contract import build_review_workbench_apply_executor_contract
from .gui_review_workbench_executor_handoff_panel import build_review_workbench_executor_handoff_panel
from .gui_review_workbench_stateful_rebuild import build_review_workbench_stateful_rebuild_loop_contract
from .gui_review_workbench_stateful_callbacks import build_review_workbench_stateful_callback_plan
from .gui_review_workbench_table_model import build_review_workbench_table_model
from .gui_review_workbench_view_models import build_ui_review_workbench_view_model

REVIEW_WORKBENCH_SERVICE_SCHEMA_VERSION = "1.0"
REVIEW_WORKBENCH_SERVICE_KIND = "gui_review_workbench_service_bundle"


def _now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


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


def _read_json_object(path: str | Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in {path}")
    return payload


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(dict(payload), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _people_summary_from_bundle(bundle_dir: str | Path | None) -> dict[str, object]:
    if bundle_dir is None:
        return {}
    root = Path(bundle_dir)
    summary: dict[str, object] = {"bundle_dir": str(root), "ready_for_gui": False}
    manifest_path = root / "bundle_manifest.json"
    workspace_path = root / "people_review_workspace.json"
    workflow_path = root / "people_review_workflow.json"
    assets_path = root / "assets" / "people_review_assets.json"
    if manifest_path.exists():
        try:
            manifest = _read_json_object(manifest_path)
        except (OSError, ValueError, json.JSONDecodeError):
            manifest = {}
        manifest_summary = _as_mapping(manifest.get("summary"))
        summary.update({k: v for k, v in manifest_summary.items() if isinstance(k, str)})
        summary["manifest_status"] = manifest.get("status")
    if workspace_path.exists():
        try:
            workspace = _read_json_object(workspace_path)
        except (OSError, ValueError, json.JSONDecodeError):
            workspace = {}
        groups = workspace.get("groups") if isinstance(workspace.get("groups"), list) else []
        cards = workspace.get("cards") if isinstance(workspace.get("cards"), list) else []
        faces = workspace.get("faces") if isinstance(workspace.get("faces"), list) else []
        summary.setdefault("group_count", len(groups) if groups else len(cards))
        summary.setdefault("face_count", len(faces))
        summary["workspace_path"] = str(workspace_path)
    summary["ready_for_gui"] = workspace_path.exists() and workflow_path.exists()
    summary["has_assets"] = assets_path.exists()
    return summary


def _default_input_summary(name: str) -> dict[str, object]:
    return {"kind": f"empty_{name}_summary", "run_count": 0, "review_candidate_count": 0, "error_count": 0}


def build_gui_review_workbench_service_bundle(
    *,
    duplicate_review: Mapping[str, Any] | None = None,
    similar_images: Mapping[str, Any] | None = None,
    decision_summary: Mapping[str, Any] | None = None,
    people_review_summary: Mapping[str, Any] | None = None,
    people_bundle_dir: str | Path | None = None,
    reviewed_decision_plan: Mapping[str, Any] | None = None,
    selected_lane_id: str | None = None,
    lane_status_filter: str = "all",
    lane_query: str = "",
    lane_sort_mode: str = "attention_first",
    page: int = 1,
    page_size: int = 20,
) -> dict[str, object]:
    """Build the full headless Review Workbench payload a Qt UI can consume.

    The bundle intentionally stays non-executing: it summarizes review lanes,
    table state, command-safe action metadata, and a Qt adapter package without
    importing PySide6 or opening a window.
    """

    duplicate_model = dict(duplicate_review or _default_input_summary("duplicate_review"))
    similar_model = dict(similar_images or _default_input_summary("similar_images"))
    decision_model = dict(decision_summary or _default_input_summary("decision_summary"))
    people_model = dict(people_review_summary or _people_summary_from_bundle(people_bundle_dir))

    view_model = build_ui_review_workbench_view_model(
        duplicate_review=duplicate_model,
        similar_images=similar_model,
        decision_summary=decision_model,
        people_review_summary=people_model,
        selected_lane_id=selected_lane_id,
        lane_status_filter=lane_status_filter,
        lane_query=lane_query,
        lane_sort_mode=lane_sort_mode,
    )
    sorted_filtered_lanes = [dict(item) for item in view_model.get("sorted_filtered_lanes", []) if isinstance(item, Mapping)]
    selected_lane_id_value = str(view_model.get("selected_lane_id") or "") or None
    table_model = build_review_workbench_table_model(
        sorted_filtered_lanes,
        selected_lane_id=selected_lane_id_value,
        page=page,
        page_size=page_size,
    )
    controller_state = build_review_workbench_view_state(
        duplicate_review=duplicate_model,
        similar_images=similar_model,
        decision_summary=decision_model,
        people_review_summary=people_model,
        selected_lane_id=selected_lane_id_value,
        lane_status_filter=lane_status_filter,
        lane_query=lane_query,
        lane_sort_mode=lane_sort_mode,
        page=page,
        page_size=page_size,
    )
    action_plan = build_review_workbench_action_plan(view_model)
    qt_workbench = build_qt_review_workbench(
        page_model=view_model,
        pending_changes=(),
        workspace_path=str(Path(people_bundle_dir) / "people_review_workspace.json") if people_bundle_dir else None,
    )
    adapter_package = build_qt_review_workbench_adapter_package(
        view_model=view_model,
        table_model=table_model,
        action_plan=action_plan,
        controller_state=controller_state,
        qt_workbench=qt_workbench,
    )
    widget_binding_plan = build_qt_review_workbench_widget_binding_plan(adapter_package)
    widget_skeleton = build_qt_review_workbench_widget_skeleton(widget_binding_plan)
    view_summary = _as_mapping(view_model.get("summary"))
    table_summary = _as_mapping(table_model.get("summary"))
    adapter_summary = _as_mapping(adapter_package.get("summary"))
    widget_binding_summary = _as_mapping(widget_binding_plan.get("summary"))
    widget_skeleton_summary = _as_mapping(widget_skeleton.get("summary"))
    capabilities = {
        "headless_testable": True,
        "requires_pyside6": False,
        "opens_window": False,
        "executes_commands": False,
        "local_only": True,
        "apply_enabled": False,
        "qt_adapter_ready": bool(adapter_package.get("ready")),
        "qt_widget_binding_ready": bool(widget_binding_plan.get("ready")),
        "qt_widget_skeleton_ready": bool(widget_skeleton.get("ready")),
    }
    base_ready = (
        capabilities["qt_adapter_ready"] is True
        and capabilities["qt_widget_binding_ready"] is True
        and capabilities["qt_widget_skeleton_ready"] is True
        and _as_mapping(action_plan.get("capabilities")).get("executes_commands") is False
        and _as_mapping(table_model.get("capabilities")).get("executes_commands") is False
    )
    interaction_source_bundle = {
        "view_model": view_model,
        "table_model": table_model,
        "controller_state": controller_state,
        "action_plan": action_plan,
        "qt_adapter_package": adapter_package,
        "qt_widget_skeleton": widget_skeleton,
        "readiness": {"ready": base_ready, "status": "ready" if base_ready else "blocked"},
    }
    interaction_plan = build_review_workbench_interaction_plan(interaction_source_bundle)
    callback_source_bundle = {**interaction_source_bundle, "interaction_plan": interaction_plan}
    callback_mount_plan = build_review_workbench_callback_mount_plan(callback_source_bundle)
    apply_preview_source_bundle = {**callback_source_bundle, "callback_mount_plan": callback_mount_plan}
    apply_preview = build_review_workbench_apply_preview(apply_preview_source_bundle, reviewed_decision_plan=reviewed_decision_plan)
    confirmation_dialog = build_review_workbench_confirmation_dialog_model(apply_preview)
    apply_executor_contract = build_review_workbench_apply_executor_contract(confirmation_dialog)
    executor_handoff_panel = build_review_workbench_executor_handoff_panel(confirmation_dialog, apply_executor_contract)
    stateful_rebuild_loop = build_review_workbench_stateful_rebuild_loop_contract(
        {
            "view_model": view_model,
            "table_model": table_model,
            "controller_state": controller_state,
            "interaction_plan": interaction_plan,
            "capabilities": capabilities,
        }
    )
    stateful_callback_plan = build_review_workbench_stateful_callback_plan(
        {
            "callback_mount_plan": callback_mount_plan,
            "stateful_rebuild_loop": stateful_rebuild_loop,
        }
    )
    interaction_summary = _as_mapping(interaction_plan.get("summary"))
    callback_summary = _as_mapping(callback_mount_plan.get("summary"))
    apply_preview_summary = _as_mapping(apply_preview.get("summary"))
    confirmation_dialog_summary = _as_mapping(confirmation_dialog.get("summary"))
    apply_executor_summary = _as_mapping(apply_executor_contract.get("summary"))
    executor_handoff_summary = _as_mapping(executor_handoff_panel.get("summary"))
    stateful_rebuild_summary = _as_mapping(stateful_rebuild_loop.get("summary"))
    stateful_callback_summary = _as_mapping(stateful_callback_plan.get("summary"))
    capabilities["qt_interaction_plan_ready"] = bool(interaction_plan.get("ready"))
    capabilities["qt_callback_mount_plan_ready"] = bool(callback_mount_plan.get("ready"))
    capabilities["review_workbench_apply_preview_available"] = True
    capabilities["review_workbench_apply_preview_ready"] = bool(_as_mapping(apply_preview.get("readiness")).get("ready"))
    capabilities["review_workbench_confirmation_dialog_available"] = True
    capabilities["review_workbench_confirmation_dialog_ready"] = bool(_as_mapping(confirmation_dialog.get("readiness")).get("ready"))
    capabilities["review_workbench_apply_executor_contract_available"] = True
    capabilities["review_workbench_apply_executor_contract_ready"] = bool(_as_mapping(apply_executor_contract.get("readiness")).get("ready"))
    capabilities["review_workbench_executor_handoff_panel_available"] = True
    capabilities["review_workbench_executor_handoff_panel_ready"] = bool(_as_mapping(executor_handoff_panel.get("readiness")).get("ready"))
    capabilities["review_workbench_stateful_rebuild_loop_ready"] = bool(_as_mapping(stateful_rebuild_loop.get("readiness")).get("ready"))
    capabilities["review_workbench_stateful_callback_plan_ready"] = bool(_as_mapping(stateful_callback_plan.get("readiness")).get("ready"))
    ready = (
        base_ready
        and capabilities["qt_interaction_plan_ready"] is True
        and capabilities["qt_callback_mount_plan_ready"] is True
        and capabilities["review_workbench_stateful_rebuild_loop_ready"] is True
        and capabilities["review_workbench_stateful_callback_plan_ready"] is True
    )
    return {
        "schema_version": REVIEW_WORKBENCH_SERVICE_SCHEMA_VERSION,
        "kind": REVIEW_WORKBENCH_SERVICE_KIND,
        "generated_at_utc": _now_utc(),
        "inputs": {
            "has_duplicate_review": bool(duplicate_review),
            "has_similar_images": bool(similar_images),
            "has_decision_summary": bool(decision_summary),
            "has_people_review_summary": bool(people_review_summary) or bool(people_model),
            "has_reviewed_decision_plan": bool(reviewed_decision_plan),
            "people_bundle_dir": str(people_bundle_dir) if people_bundle_dir is not None else None,
            "selected_lane_id": selected_lane_id,
            "lane_status_filter": lane_status_filter,
            "lane_query": lane_query,
            "lane_sort_mode": lane_sort_mode,
            "page": page,
            "page_size": page_size,
        },
        "view_model": view_model,
        "table_model": table_model,
        "controller_state": controller_state,
        "action_plan": action_plan,
        "qt_workbench": qt_workbench,
        "qt_adapter_package": adapter_package,
        "qt_widget_binding_plan": widget_binding_plan,
        "qt_widget_skeleton": widget_skeleton,
        "interaction_plan": interaction_plan,
        "callback_mount_plan": callback_mount_plan,
        "apply_preview": apply_preview,
        "confirmation_dialog": confirmation_dialog,
        "apply_executor_contract": apply_executor_contract,
        "executor_handoff_panel": executor_handoff_panel,
        "stateful_rebuild_loop": stateful_rebuild_loop,
        "stateful_callback_plan": stateful_callback_plan,
        "capabilities": capabilities,
        "readiness": {
            "ready": ready,
            "status": "ready" if ready else "blocked",
            "next_action": (
                "The Review Workbench widget skeleton, interaction plan, and callback mounts are ready for lazy PySide6 mounting."
                if ready
                else "Fix adapter/widget/action/table safety checks before adding a real Qt widget."
            ),
        },
        "summary": {
            "lane_count": view_summary.get("lane_count", 0),
            "attention_count": view_summary.get("attention_count", 0),
            "selected_lane_id": view_summary.get("selected_lane_id"),
            "table_row_count": table_summary.get("row_count", 0),
            "qt_component_count": adapter_summary.get("component_count", 0),
            "qt_widget_binding_count": widget_binding_summary.get("widget_binding_count", 0),
            "qt_action_binding_count": widget_binding_summary.get("action_binding_count", 0),
            "qt_widget_skeleton_node_count": widget_skeleton_summary.get("node_count", 0),
            "qt_widget_skeleton_route_wire_count": widget_skeleton_summary.get("route_wire_count", 0),
            "interaction_intent_count": interaction_summary.get("intent_count", 0),
            "interaction_signal_binding_count": interaction_summary.get("signal_binding_count", 0),
            "interaction_toolbar_binding_count": interaction_summary.get("toolbar_binding_count", 0),
            "callback_mount_count": callback_summary.get("callback_mount_count", 0),
            "enabled_callback_mount_count": callback_summary.get("enabled_callback_mount_count", 0),
            "disabled_callback_mount_count": callback_summary.get("disabled_callback_mount_count", 0),
            "apply_preview_ready": apply_preview_summary.get("preview_ready", False),
            "apply_preview_candidate_command_count": apply_preview_summary.get("candidate_command_count", 0),
            "apply_preview_status": apply_preview_summary.get("status"),
            "confirmation_dialog_status": confirmation_dialog_summary.get("status"),
            "confirmation_dialog_risk_level": confirmation_dialog_summary.get("risk_level"),
            "confirmation_dialog_required_check_count": confirmation_dialog_summary.get("required_check_count", 0),
            "confirmation_dialog_required_satisfied_count": confirmation_dialog_summary.get("required_satisfied_count", 0),
            "apply_executor_contract_status": apply_executor_summary.get("status"),
            "apply_executor_contract_preflight_failed_check_count": apply_executor_summary.get("preflight_failed_check_count", 0),
            "apply_executor_contract_ready_for_future_executor": apply_executor_summary.get("ready_for_future_executor", False),
            "executor_handoff_panel_status": executor_handoff_summary.get("status"),
            "executor_handoff_panel_section_count": executor_handoff_summary.get("section_count", 0),
            "executor_handoff_panel_dry_run_command_count": executor_handoff_summary.get("dry_run_command_count", 0),
            "executor_handoff_panel_audit_row_count": executor_handoff_summary.get("audit_row_count", 0),
            "stateful_rebuild_loop_status": stateful_rebuild_summary.get("status"),
            "stateful_rebuild_loop_intent_count": stateful_rebuild_summary.get("stateful_intent_count", 0),
            "stateful_rebuild_loop_current_selected_lane_id": stateful_rebuild_summary.get("current_selected_lane_id"),
            "stateful_callback_plan_status": stateful_callback_summary.get("status"),
            "stateful_callback_page_rebuild_count": stateful_callback_summary.get("page_rebuild_callback_count", 0),
            "enabled_action_count": _as_int(action_plan.get("enabled_action_count")),
            "apply_enabled": False,
            "status": "needs_review" if _as_int(view_summary.get("attention_count")) > 0 else "ready",
        },
        "artifact_names": [
            "review_workbench_service_bundle.json",
            "review_workbench_view_model.json",
            "review_workbench_table_model.json",
            "review_workbench_controller_state.json",
            "review_workbench_action_plan.json",
            "review_workbench_qt_workbench.json",
            "review_workbench_qt_adapter_package.json",
            "review_workbench_qt_widget_binding_plan.json",
            "review_workbench_qt_widget_skeleton.json",
            "review_workbench_interaction_plan.json",
            "review_workbench_callback_mount_plan.json",
            "review_workbench_apply_preview.json",
            "review_workbench_confirmation_dialog_model.json",
            "review_workbench_apply_executor_contract.json",
            "review_workbench_apply_executor_handoff_panel.json",
            "review_workbench_stateful_rebuild_loop.json",
            "review_workbench_stateful_callback_plan.json",
        ],
    }


def write_gui_review_workbench_service_bundle(out_dir: str | Path, **kwargs: Any) -> dict[str, object]:
    root = Path(out_dir)
    root.mkdir(parents=True, exist_ok=True)
    bundle = build_gui_review_workbench_service_bundle(**kwargs)
    artifacts: list[tuple[str, Mapping[str, Any]]] = [
        ("review_workbench_view_model.json", _as_mapping(bundle.get("view_model"))),
        ("review_workbench_table_model.json", _as_mapping(bundle.get("table_model"))),
        ("review_workbench_controller_state.json", _as_mapping(bundle.get("controller_state"))),
        ("review_workbench_action_plan.json", _as_mapping(bundle.get("action_plan"))),
        ("review_workbench_qt_workbench.json", _as_mapping(bundle.get("qt_workbench"))),
        ("review_workbench_qt_adapter_package.json", _as_mapping(bundle.get("qt_adapter_package"))),
        ("review_workbench_qt_widget_binding_plan.json", _as_mapping(bundle.get("qt_widget_binding_plan"))),
        ("review_workbench_qt_widget_skeleton.json", _as_mapping(bundle.get("qt_widget_skeleton"))),
        ("review_workbench_interaction_plan.json", _as_mapping(bundle.get("interaction_plan"))),
        ("review_workbench_callback_mount_plan.json", _as_mapping(bundle.get("callback_mount_plan"))),
        ("review_workbench_apply_preview.json", _as_mapping(bundle.get("apply_preview"))),
        ("review_workbench_confirmation_dialog_model.json", _as_mapping(bundle.get("confirmation_dialog"))),
        ("review_workbench_apply_executor_contract.json", _as_mapping(bundle.get("apply_executor_contract"))),
        ("review_workbench_apply_executor_handoff_panel.json", _as_mapping(bundle.get("executor_handoff_panel"))),
        ("review_workbench_stateful_rebuild_loop.json", _as_mapping(bundle.get("stateful_rebuild_loop"))),
        ("review_workbench_stateful_callback_plan.json", _as_mapping(bundle.get("stateful_callback_plan"))),
        ("review_workbench_service_bundle.json", bundle),
    ]
    written_files: list[str] = []
    for filename, payload in artifacts:
        path = root / filename
        _write_json(path, payload)
        written_files.append(str(path))
    readme_path = root / "README.txt"
    readme_path.write_text(
        "Review Workbench headless Qt adapter bundle\n"
        "Generated by media-manager app-services review-workbench.\n"
        "The payload is local-only, does not import PySide6, does not open a window, and does not execute media operations.\n",
        encoding="utf-8",
    )
    written_files.append(str(readme_path))
    return {
        **bundle,
        "output_dir": str(root),
        "written_file_count": len(written_files),
        "written_files": written_files,
    }


__all__ = [
    "REVIEW_WORKBENCH_SERVICE_KIND",
    "REVIEW_WORKBENCH_SERVICE_SCHEMA_VERSION",
    "build_gui_review_workbench_service_bundle",
    "write_gui_review_workbench_service_bundle",
]
