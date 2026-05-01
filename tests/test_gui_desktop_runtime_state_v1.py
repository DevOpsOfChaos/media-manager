from __future__ import annotations

import json
import sys
from pathlib import Path

from media_manager.core.gui_desktop_runtime_state import (
    build_gui_desktop_runtime_state,
    summarize_gui_desktop_runtime_state,
    write_gui_desktop_runtime_state,
)


def test_desktop_runtime_state_builds_full_ui_contract_without_qt_import() -> None:
    sys.modules.pop("PySide6", None)
    state = build_gui_desktop_runtime_state(active_page_id="dashboard", language="en")
    assert state["kind"] == "gui_desktop_runtime_state"
    assert state["summary"]["active_page_id"] == "dashboard"
    assert state["shell_model"]["page"]["kind"] == "dashboard_page"
    assert state["visible_desktop_plan"]["kind"] == "qt_visible_desktop_plan"
    assert state["render_bridge"]["kind"] == "qt_render_bridge"
    assert state["view_orchestration"]["kind"] == "qt_view_orchestration_state"
    assert state["app_service_view_models"]["summary"]["view_model_count"] == 7
    assert state["app_contract_bindings"]["readiness"]["ready"] is True
    assert state["review_workbench_service"]["qt_widget_binding_plan"]["readiness"]["ready"] is True
    assert state["review_workbench_service"]["apply_preview"]["capabilities"]["executes_commands"] is False
    assert state["review_workbench_service"]["confirmation_dialog"]["capabilities"]["executes_commands"] is False
    assert state["review_workbench_service"]["executor_handoff_panel"]["capabilities"]["executes_commands"] is False
    assert state["readiness"]["ready"] is True
    assert state["capabilities"]["requires_pyside6"] is False
    assert state["capabilities"]["opens_window"] is False
    assert state["capabilities"]["executes_commands"] is False
    assert "PySide6" not in sys.modules


def test_desktop_runtime_state_supports_product_pages() -> None:
    for page_id in ("new-run", "people-review", "run-history", "profiles", "settings"):
        state = build_gui_desktop_runtime_state(active_page_id=page_id)
        assert state["summary"]["active_page_id"] == page_id
        assert state["readiness"]["ready"] is True


def test_desktop_runtime_state_normalizes_settings_doctor_alias() -> None:
    state = build_gui_desktop_runtime_state(active_page_id="settings-doctor")
    assert state["summary"]["active_page_id"] == "settings"
    assert state["summary"]["page_kind"] == "settings_page"
    assert state["readiness"]["ready"] is True


def test_desktop_runtime_state_summary_is_human_readable() -> None:
    state = build_gui_desktop_runtime_state(active_page_id="profiles", language="de")
    summary = summarize_gui_desktop_runtime_state(state)
    assert "Media Manager desktop runtime state" in summary
    assert "Active page: profiles" in summary
    assert "UI view models: 7" in summary
    assert "App contracts bound:" in summary
    assert "Review workbench Qt widget bindings:" in summary
    assert "Review workbench apply preview:" in summary
    assert "Review workbench confirmation dialog:" in summary
    assert "Executes commands: False" in summary


def test_write_desktop_runtime_state_writes_split_payloads(tmp_path: Path) -> None:
    payload = write_gui_desktop_runtime_state(tmp_path / "desktop", active_page_id="dashboard")
    assert payload["written_file_count"] == 19
    for name in [
        "desktop_runtime_state.json",
        "shell_model.json",
        "visible_desktop_plan.json",
        "qt_render_bridge.json",
        "page_controller.json",
        "view_orchestration.json",
        "ui_app_service_view_models.json",
        "app_contract_bindings.json",
        "review_workbench_service.json",
        "review_workbench_qt_widget_binding_plan.json",
        "review_workbench_qt_widget_skeleton.json",
        "review_workbench_interaction_plan.json",
        "review_workbench_callback_mount_plan.json",
        "review_workbench_apply_preview.json",
        "review_workbench_confirmation_dialog_model.json",
        "review_workbench_apply_executor_contract.json",
        "review_workbench_apply_executor_handoff_panel.json",
        "review_workbench_stateful_rebuild_loop.json",
        "README.txt",
    ]:
        assert (tmp_path / "desktop" / name).exists()
    written = json.loads((tmp_path / "desktop" / "desktop_runtime_state.json").read_text(encoding="utf-8"))
    assert written["readiness"]["ready"] is True
