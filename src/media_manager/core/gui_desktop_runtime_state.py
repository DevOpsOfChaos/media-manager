from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

from .gui_app_contract_bindings import build_gui_app_contract_bindings
from .gui_app_service_view_models import build_ui_app_service_view_models
from .gui_page_contracts import build_gui_navigation_state, build_gui_page_catalog
from .gui_review_workbench_service import build_gui_review_workbench_service_bundle
from .gui_qt_page_controller import build_page_controller_state
from .gui_qt_render_bridge import build_qt_render_bridge
from .gui_qt_view_orchestrator import build_qt_view_orchestration_state
from .gui_qt_visible_desktop_plan import build_qt_visible_desktop_plan, desktop_plan_is_ready
from .gui_shell_model import build_gui_shell_model_from_paths

DESKTOP_RUNTIME_STATE_SCHEMA_VERSION = "1.0"
DESKTOP_RUNTIME_STATE_KIND = "gui_desktop_runtime_state"


def _now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _as_mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _as_list(value: object) -> list[Any]:
    return value if isinstance(value, list) else []


def _count_navigation_items(payload: Mapping[str, Any]) -> int:
    return len([item for item in _as_list(payload.get("navigation")) if isinstance(item, Mapping)])


def _runtime_capabilities(
    *,
    shell_model: Mapping[str, Any],
    visible_desktop_plan: Mapping[str, Any],
    render_bridge: Mapping[str, Any],
    orchestration_state: Mapping[str, Any],
    app_service_view_models: Mapping[str, Any],
    app_contract_bindings: Mapping[str, Any],
    review_workbench_service: Mapping[str, Any],
) -> dict[str, object]:
    bridge_capabilities = _as_mapping(render_bridge.get("capabilities"))
    shell_capabilities = _as_mapping(shell_model.get("capabilities"))
    return {
        "headless_testable": True,
        "requires_pyside6": False,
        "opens_window": False,
        "executes_commands": False,
        "local_only": True,
        "qt_shell": bool(shell_capabilities.get("qt_shell")),
        "modern_ui": bool(shell_capabilities.get("modern_ui")),
        "bilingual_ui": bool(shell_capabilities.get("bilingual_ui")),
        "visible_desktop_ready": desktop_plan_is_ready(visible_desktop_plan),
        "render_bridge_ready": bool(render_bridge.get("ready")),
        "view_orchestration_ready": bool(orchestration_state.get("ready")),
        "bridge_declares_no_window": bridge_capabilities.get("opens_window") is False,
        "bridge_declares_no_execution": bridge_capabilities.get("executes_commands") is False,
        "app_service_view_models_ready": _as_mapping(app_service_view_models.get("capabilities")).get("executes_commands") is False,
        "app_contract_bindings_ready": _as_mapping(app_contract_bindings.get("readiness")).get("ready") is True,
        "review_workbench_adapter_ready": _as_mapping(review_workbench_service.get("readiness")).get("ready") is True,
        "review_workbench_widget_bindings_ready": _as_mapping(_as_mapping(review_workbench_service.get("qt_widget_binding_plan")).get("readiness")).get("ready") is True,
        "review_workbench_widget_skeleton_ready": _as_mapping(_as_mapping(review_workbench_service.get("qt_widget_skeleton")).get("readiness")).get("ready") is True,
        "review_workbench_interaction_plan_ready": _as_mapping(_as_mapping(review_workbench_service.get("interaction_plan")).get("readiness")).get("ready") is True,
        "review_workbench_callback_mount_plan_ready": _as_mapping(_as_mapping(review_workbench_service.get("callback_mount_plan")).get("readiness")).get("ready") is True,
        "review_workbench_apply_preview_available": bool(review_workbench_service.get("apply_preview")),
        "review_workbench_apply_preview_executes_commands": _as_mapping(_as_mapping(review_workbench_service.get("apply_preview")).get("capabilities")).get("executes_commands") is True,
        "review_workbench_confirmation_dialog_available": bool(review_workbench_service.get("confirmation_dialog")),
        "review_workbench_confirmation_dialog_executes_commands": _as_mapping(_as_mapping(review_workbench_service.get("confirmation_dialog")).get("capabilities")).get("executes_commands") is True,
        "review_workbench_apply_executor_contract_available": bool(review_workbench_service.get("apply_executor_contract")),
        "review_workbench_apply_executor_contract_executes_commands": _as_mapping(_as_mapping(review_workbench_service.get("apply_executor_contract")).get("capabilities")).get("executes_commands") is True,
    }


def _readiness(
    *,
    shell_model: Mapping[str, Any],
    visible_desktop_plan: Mapping[str, Any],
    render_bridge: Mapping[str, Any],
    orchestration_state: Mapping[str, Any],
    app_service_view_models: Mapping[str, Any],
    app_contract_bindings: Mapping[str, Any],
    review_workbench_service: Mapping[str, Any],
    capabilities: Mapping[str, Any],
) -> dict[str, object]:
    navigation_count = _count_navigation_items(shell_model)
    checks = [
        {
            "id": "shell-model",
            "label": "GUI shell model can be built",
            "ok": bool(shell_model.get("active_page_id")) and bool(_as_mapping(shell_model.get("page")).get("page_id")),
        },
        {"id": "navigation", "label": "Navigation has at least one item", "ok": navigation_count > 0},
        {"id": "visible-desktop-plan", "label": "Visible desktop plan is ready", "ok": desktop_plan_is_ready(visible_desktop_plan)},
        {"id": "render-bridge", "label": "Qt render bridge is ready", "ok": bool(render_bridge.get("ready"))},
        {"id": "view-orchestration", "label": "View orchestration accepts the shell model", "ok": bool(orchestration_state.get("ready"))},
        {
            "id": "app-service-view-models",
            "label": "Product UI view models are available for Qt binding",
            "ok": bool(_as_mapping(app_service_view_models.get("view_models")).get("scan_setup")),
        },
        {
            "id": "app-contract-bindings",
            "label": "App-service contracts are bound to explicit GUI surfaces",
            "ok": bool(_as_mapping(app_contract_bindings.get("readiness")).get("ready")),
        },
        {
            "id": "review-workbench-adapter",
            "label": "Review Workbench exposes a Qt-ready adapter package",
            "ok": bool(_as_mapping(review_workbench_service.get("readiness")).get("ready")),
        },
        {
            "id": "review-workbench-widget-bindings",
            "label": "Review Workbench adapter components are mapped to explicit Qt widget bindings",
            "ok": bool(_as_mapping(_as_mapping(review_workbench_service.get("qt_widget_binding_plan")).get("readiness")).get("ready")),
        },
        {
            "id": "review-workbench-widget-skeleton",
            "label": "Review Workbench has a lazy Qt widget skeleton for runtime mounting",
            "ok": bool(_as_mapping(_as_mapping(review_workbench_service.get("qt_widget_skeleton")).get("readiness")).get("ready")),
        },
        {
            "id": "review-workbench-interactions",
            "label": "Review Workbench Qt signals and toolbar actions are mapped to non-executing interaction intents",
            "ok": bool(_as_mapping(_as_mapping(review_workbench_service.get("interaction_plan")).get("readiness")).get("ready")),
        },
        {
            "id": "review-workbench-callback-mounts",
            "label": "Review Workbench Qt widgets expose concrete callback mounts for local intent dispatch",
            "ok": bool(_as_mapping(_as_mapping(review_workbench_service.get("callback_mount_plan")).get("readiness")).get("ready")),
        },
        {
            "id": "review-workbench-apply-preview",
            "label": "Review Workbench exposes a non-executing apply preview contract",
            "ok": bool(review_workbench_service.get("apply_preview"))
            and _as_mapping(_as_mapping(review_workbench_service.get("apply_preview")).get("capabilities")).get("executes_commands") is False,
        },
        {
            "id": "review-workbench-confirmation-dialog",
            "label": "Review Workbench exposes a guarded non-executing confirmation dialog model",
            "ok": bool(review_workbench_service.get("confirmation_dialog"))
            and _as_mapping(_as_mapping(review_workbench_service.get("confirmation_dialog")).get("capabilities")).get("executes_commands") is False,
        },
        {
            "id": "review-workbench-apply-executor-contract",
            "label": "Review Workbench exposes a disabled-by-default non-executing apply executor contract",
            "ok": bool(review_workbench_service.get("apply_executor_contract"))
            and _as_mapping(_as_mapping(review_workbench_service.get("apply_executor_contract")).get("capabilities")).get("executes_commands") is False,
        },
        {
            "id": "review-workbench-executor-handoff-panel",
            "label": "Review Workbench exposes a display-only confirmation/executor handoff panel",
            "ok": bool(review_workbench_service.get("executor_handoff_panel"))
            and _as_mapping(_as_mapping(review_workbench_service.get("executor_handoff_panel")).get("capabilities")).get("executes_commands") is False,
        },
        {
            "id": "review-workbench-stateful-rebuild-loop",
            "label": "Review Workbench exposes a non-executing stateful rebuild loop for local UI intents",
            "ok": bool(review_workbench_service.get("stateful_rebuild_loop"))
            and _as_mapping(_as_mapping(review_workbench_service.get("stateful_rebuild_loop")).get("capabilities")).get("executes_commands") is False,
        },
        {
            "id": "headless-safe",
            "label": "No PySide6 import, no window and no command execution are required",
            "ok": (
                capabilities.get("requires_pyside6") is False
                and capabilities.get("opens_window") is False
                and capabilities.get("executes_commands") is False
                and capabilities.get("local_only") is True
            ),
        },
    ]
    failed = [item for item in checks if not item.get("ok")]
    return {
        "ready": not failed,
        "status": "ready" if not failed else "blocked",
        "check_count": len(checks),
        "failed_check_count": len(failed),
        "checks": checks,
        "next_action": (
            "The desktop runtime state is ready for a real Qt widget binding step."
            if not failed
            else "Fix the failing desktop runtime checks before wiring real widgets."
        ),
    }


def _summary(
    *,
    shell_model: Mapping[str, Any],
    visible_desktop_plan: Mapping[str, Any],
    render_bridge: Mapping[str, Any],
    orchestration_state: Mapping[str, Any],
    app_service_view_models: Mapping[str, Any],
    app_contract_bindings: Mapping[str, Any],
    review_workbench_service: Mapping[str, Any],
    readiness: Mapping[str, Any],
) -> dict[str, object]:
    page = _as_mapping(shell_model.get("page"))
    desktop_summary = _as_mapping(visible_desktop_plan.get("summary"))
    bridge_summary = _as_mapping(render_bridge.get("summary"))
    validation = _as_mapping(orchestration_state.get("validation"))
    contract_summary = _as_mapping(app_contract_bindings.get("summary"))
    contract_readiness = _as_mapping(app_contract_bindings.get("readiness"))
    review_summary = _as_mapping(review_workbench_service.get("summary"))
    widget_binding_summary = _as_mapping(_as_mapping(review_workbench_service.get("qt_widget_binding_plan")).get("summary"))
    widget_skeleton_summary = _as_mapping(_as_mapping(review_workbench_service.get("qt_widget_skeleton")).get("summary"))
    interaction_summary = _as_mapping(_as_mapping(review_workbench_service.get("interaction_plan")).get("summary"))
    callback_summary = _as_mapping(_as_mapping(review_workbench_service.get("callback_mount_plan")).get("summary"))
    apply_preview_summary = _as_mapping(_as_mapping(review_workbench_service.get("apply_preview")).get("summary"))
    confirmation_dialog_summary = _as_mapping(_as_mapping(review_workbench_service.get("confirmation_dialog")).get("summary"))
    apply_executor_summary = _as_mapping(_as_mapping(review_workbench_service.get("apply_executor_contract")).get("summary"))
    executor_handoff_summary = _as_mapping(_as_mapping(review_workbench_service.get("executor_handoff_panel")).get("summary"))
    stateful_rebuild_summary = _as_mapping(_as_mapping(review_workbench_service.get("stateful_rebuild_loop")).get("summary"))
    return {
        "active_page_id": shell_model.get("active_page_id"),
        "page_kind": page.get("kind"),
        "page_title": page.get("title"),
        "language": shell_model.get("language"),
        "theme": _as_mapping(shell_model.get("theme")).get("theme"),
        "density": _as_mapping(shell_model.get("layout")).get("density"),
        "navigation_count": _count_navigation_items(shell_model),
        "visible_body_kind": desktop_summary.get("body_kind"),
        "render_node_count": bridge_summary.get("node_count"),
        "sensitive_node_count": bridge_summary.get("sensitive_node_count"),
        "contract_error_count": len(_as_list(validation.get("errors"))),
        "app_service_view_model_count": _as_mapping(app_service_view_models.get("summary")).get("view_model_count"),
        "app_contract_count": app_contract_bindings.get("contract_count"),
        "app_contract_fully_bound_count": contract_summary.get("fully_bound_contract_count"),
        "app_contract_binding_status": contract_readiness.get("status"),
        "review_workbench_lane_count": review_summary.get("lane_count"),
        "review_workbench_qt_component_count": review_summary.get("qt_component_count"),
        "review_workbench_qt_widget_binding_count": review_summary.get("qt_widget_binding_count"),
        "review_workbench_qt_action_binding_count": review_summary.get("qt_action_binding_count"),
        "review_workbench_qt_widget_skeleton_node_count": review_summary.get("qt_widget_skeleton_node_count"),
        "review_workbench_qt_widget_skeleton_route_wire_count": review_summary.get("qt_widget_skeleton_route_wire_count"),
        "review_workbench_interaction_intent_count": review_summary.get("interaction_intent_count"),
        "review_workbench_interaction_signal_binding_count": review_summary.get("interaction_signal_binding_count"),
        "review_workbench_interaction_status": interaction_summary.get("status"),
        "review_workbench_callback_mount_count": review_summary.get("callback_mount_count"),
        "review_workbench_enabled_callback_mount_count": review_summary.get("enabled_callback_mount_count"),
        "review_workbench_callback_mount_status": callback_summary.get("status"),
        "review_workbench_apply_preview_ready": apply_preview_summary.get("preview_ready"),
        "review_workbench_apply_preview_status": apply_preview_summary.get("status"),
        "review_workbench_apply_preview_candidate_command_count": apply_preview_summary.get("candidate_command_count"),
        "review_workbench_confirmation_dialog_status": confirmation_dialog_summary.get("status"),
        "review_workbench_confirmation_dialog_risk_level": confirmation_dialog_summary.get("risk_level"),
        "review_workbench_confirmation_dialog_required_check_count": confirmation_dialog_summary.get("required_check_count"),
        "review_workbench_confirmation_dialog_required_satisfied_count": confirmation_dialog_summary.get("required_satisfied_count"),
        "review_workbench_apply_executor_contract_status": apply_executor_summary.get("status"),
        "review_workbench_apply_executor_contract_ready_for_future_executor": apply_executor_summary.get("ready_for_future_executor"),
        "review_workbench_apply_executor_contract_failed_check_count": apply_executor_summary.get("preflight_failed_check_count"),
        "review_workbench_executor_handoff_panel_status": executor_handoff_summary.get("status"),
        "review_workbench_executor_handoff_panel_section_count": executor_handoff_summary.get("section_count"),
        "review_workbench_executor_handoff_panel_dry_run_command_count": executor_handoff_summary.get("dry_run_command_count"),
        "review_workbench_stateful_rebuild_loop_status": stateful_rebuild_summary.get("status"),
        "review_workbench_stateful_rebuild_loop_intent_count": stateful_rebuild_summary.get("stateful_intent_count"),
        "review_workbench_widget_binding_status": widget_binding_summary.get("status"),
        "review_workbench_widget_skeleton_status": widget_skeleton_summary.get("status"),
        "review_workbench_adapter_status": _as_mapping(review_workbench_service.get("readiness")).get("status"),
        "ready": bool(readiness.get("ready")),
        "status": readiness.get("status"),
    }


def build_gui_desktop_runtime_state(
    *,
    profile_dir: str | Path | None = None,
    run_dir: str | Path | None = None,
    people_bundle_dir: str | Path | None = None,
    active_page_id: str = "dashboard",
    home_state_json: str | Path | None = None,
    settings_json: str | Path | None = None,
    view_state_json: str | Path | None = None,
    language: str | None = None,
    theme: str | None = None,
    density: str | None = None,
) -> dict[str, object]:
    """Build the headless runtime state a real desktop UI can consume."""

    shell_model = build_gui_shell_model_from_paths(
        profile_dir=profile_dir,
        run_dir=run_dir,
        people_bundle_dir=people_bundle_dir,
        active_page_id=active_page_id,
        home_state_json=home_state_json,
        settings_json=settings_json,
        view_state_json=view_state_json,
        language=language,
        theme=theme,
        density=density,
    )
    page_controller = build_page_controller_state(shell_model)
    visible_desktop_plan = build_qt_visible_desktop_plan(shell_model)
    render_bridge = build_qt_render_bridge(shell_model)
    orchestration_state = build_qt_view_orchestration_state(shell_model)
    app_service_view_models = build_ui_app_service_view_models(
        _as_mapping(shell_model.get("home_state")),
        language=str(shell_model.get("language") or "en"),
        active_page_id=str(shell_model.get("active_page_id") or active_page_id),
    )
    app_contract_bindings = build_gui_app_contract_bindings()
    view_models = _as_mapping(app_service_view_models.get("view_models"))
    review_workbench_service = build_gui_review_workbench_service_bundle(
        duplicate_review=_as_mapping(view_models.get("duplicate_review")),
        similar_images=_as_mapping(view_models.get("similar_images")),
        decision_summary=_as_mapping(view_models.get("decision_summary")),
        people_bundle_dir=people_bundle_dir,
    )
    capabilities = _runtime_capabilities(
        shell_model=shell_model,
        visible_desktop_plan=visible_desktop_plan,
        render_bridge=render_bridge,
        orchestration_state=orchestration_state,
        app_service_view_models=app_service_view_models,
        app_contract_bindings=app_contract_bindings,
        review_workbench_service=review_workbench_service,
    )
    readiness = _readiness(
        shell_model=shell_model,
        visible_desktop_plan=visible_desktop_plan,
        render_bridge=render_bridge,
        orchestration_state=orchestration_state,
        app_service_view_models=app_service_view_models,
        app_contract_bindings=app_contract_bindings,
        review_workbench_service=review_workbench_service,
        capabilities=capabilities,
    )
    return {
        "schema_version": DESKTOP_RUNTIME_STATE_SCHEMA_VERSION,
        "kind": DESKTOP_RUNTIME_STATE_KIND,
        "generated_at_utc": _now_utc(),
        "shell_model": shell_model,
        "page_controller": page_controller,
        "visible_desktop_plan": visible_desktop_plan,
        "render_bridge": render_bridge,
        "view_orchestration": orchestration_state,
        "app_service_view_models": app_service_view_models,
        "app_contract_bindings": app_contract_bindings,
        "review_workbench_service": review_workbench_service,
        "page_catalog": build_gui_page_catalog(),
        "navigation_state": build_gui_navigation_state(str(shell_model.get("active_page_id") or "dashboard")),
        "capabilities": capabilities,
        "readiness": readiness,
        "summary": _summary(
            shell_model=shell_model,
            visible_desktop_plan=visible_desktop_plan,
            render_bridge=render_bridge,
            orchestration_state=orchestration_state,
            app_service_view_models=app_service_view_models,
            app_contract_bindings=app_contract_bindings,
            review_workbench_service=review_workbench_service,
            readiness=readiness,
        ),
    }


def summarize_gui_desktop_runtime_state(state: Mapping[str, Any]) -> str:
    summary = _as_mapping(state.get("summary"))
    readiness = _as_mapping(state.get("readiness"))
    capabilities = _as_mapping(state.get("capabilities"))
    return "\n".join(
        [
            "Media Manager desktop runtime state",
            f"  Active page: {summary.get('active_page_id')}",
            f"  Page kind: {summary.get('page_kind')}",
            f"  Ready: {readiness.get('ready')}",
            f"  Status: {readiness.get('status')}",
            f"  Navigation items: {summary.get('navigation_count')}",
            f"  Render nodes: {summary.get('render_node_count')}",
            f"  UI view models: {summary.get('app_service_view_model_count')}",
            f"  App contracts bound: {summary.get('app_contract_fully_bound_count')}/{summary.get('app_contract_count')}",
            f"  Review workbench Qt components: {summary.get('review_workbench_qt_component_count')}",
            f"  Review workbench Qt widget bindings: {summary.get('review_workbench_qt_widget_binding_count')}",
            f"  Review workbench Qt widget skeleton nodes: {summary.get('review_workbench_qt_widget_skeleton_node_count')}",
            f"  Review workbench interaction intents: {summary.get('review_workbench_interaction_intent_count')}",
            f"  Review workbench callback mounts: {summary.get('review_workbench_callback_mount_count')}",
            f"  Review workbench apply preview: {summary.get('review_workbench_apply_preview_status')}",
            f"  Review workbench confirmation dialog: {summary.get('review_workbench_confirmation_dialog_status')}",
            f"  Review workbench apply executor contract: {summary.get('review_workbench_apply_executor_contract_status')}",
            f"  Review workbench apply handoff panel: {summary.get('review_workbench_executor_handoff_panel_status')}",
            f"  Review workbench stateful rebuild loop: {summary.get('review_workbench_stateful_rebuild_loop_status')}",
            f"  Requires PySide6: {capabilities.get('requires_pyside6')}",
            f"  Opens window: {capabilities.get('opens_window')}",
            f"  Executes commands: {capabilities.get('executes_commands')}",
            f"  Next action: {readiness.get('next_action')}",
        ]
    )


def write_gui_desktop_runtime_state(
    out_dir: str | Path,
    *,
    profile_dir: str | Path | None = None,
    run_dir: str | Path | None = None,
    people_bundle_dir: str | Path | None = None,
    active_page_id: str = "dashboard",
    home_state_json: str | Path | None = None,
    settings_json: str | Path | None = None,
    view_state_json: str | Path | None = None,
    language: str | None = None,
    theme: str | None = None,
    density: str | None = None,
) -> dict[str, object]:
    state = build_gui_desktop_runtime_state(
        profile_dir=profile_dir,
        run_dir=run_dir,
        people_bundle_dir=people_bundle_dir,
        active_page_id=active_page_id,
        home_state_json=home_state_json,
        settings_json=settings_json,
        view_state_json=view_state_json,
        language=language,
        theme=theme,
        density=density,
    )
    root = Path(out_dir)
    root.mkdir(parents=True, exist_ok=True)
    files = {
        "desktop_runtime_state.json": state,
        "shell_model.json": _as_mapping(state.get("shell_model")),
        "visible_desktop_plan.json": _as_mapping(state.get("visible_desktop_plan")),
        "qt_render_bridge.json": _as_mapping(state.get("render_bridge")),
        "page_controller.json": _as_mapping(state.get("page_controller")),
        "view_orchestration.json": _as_mapping(state.get("view_orchestration")),
        "ui_app_service_view_models.json": _as_mapping(state.get("app_service_view_models")),
        "app_contract_bindings.json": _as_mapping(state.get("app_contract_bindings")),
        "review_workbench_service.json": _as_mapping(state.get("review_workbench_service")),
        "review_workbench_qt_widget_binding_plan.json": _as_mapping(_as_mapping(state.get("review_workbench_service")).get("qt_widget_binding_plan")),
        "review_workbench_qt_widget_skeleton.json": _as_mapping(_as_mapping(state.get("review_workbench_service")).get("qt_widget_skeleton")),
        "review_workbench_interaction_plan.json": _as_mapping(_as_mapping(state.get("review_workbench_service")).get("interaction_plan")),
        "review_workbench_callback_mount_plan.json": _as_mapping(_as_mapping(state.get("review_workbench_service")).get("callback_mount_plan")),
        "review_workbench_apply_preview.json": _as_mapping(_as_mapping(state.get("review_workbench_service")).get("apply_preview")),
        "review_workbench_confirmation_dialog_model.json": _as_mapping(_as_mapping(state.get("review_workbench_service")).get("confirmation_dialog")),
        "review_workbench_apply_executor_contract.json": _as_mapping(_as_mapping(state.get("review_workbench_service")).get("apply_executor_contract")),
        "review_workbench_apply_executor_handoff_panel.json": _as_mapping(_as_mapping(state.get("review_workbench_service")).get("executor_handoff_panel")),
        "review_workbench_stateful_rebuild_loop.json": _as_mapping(_as_mapping(state.get("review_workbench_service")).get("stateful_rebuild_loop")),
    }
    written_files: list[str] = []
    for name, payload in files.items():
        path = root / name
        path.write_text(json.dumps(dict(payload), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        written_files.append(str(path))
    readme = root / "README.txt"
    readme.write_text(
        summarize_gui_desktop_runtime_state(state)
        + "\n\nThis directory contains headless UI runtime data only. It does not contain media files, face crops, Qt widgets, or executable commands.\n",
        encoding="utf-8",
    )
    written_files.append(str(readme))
    return {**state, "output_dir": str(root), "written_files": written_files, "written_file_count": len(written_files)}


__all__ = [
    "DESKTOP_RUNTIME_STATE_KIND",
    "DESKTOP_RUNTIME_STATE_SCHEMA_VERSION",
    "build_gui_desktop_runtime_state",
    "summarize_gui_desktop_runtime_state",
    "write_gui_desktop_runtime_state",
]
