from __future__ import annotations

import json
from pathlib import Path

from media_manager.cli_app_services import main as app_services_main
from media_manager.core.app_services import build_gui_app_contract_bindings as build_via_app_services
from media_manager.core.gui_app_contract_bindings import (
    GUI_APP_CONTRACT_BINDINGS_KIND,
    build_gui_app_contract_bindings,
    list_gui_surface_bindings,
    summarize_gui_app_contract_bindings,
    write_gui_app_contract_bindings,
)
from media_manager.core.gui_desktop_runtime_state import build_gui_desktop_runtime_state, write_gui_desktop_runtime_state


def test_gui_app_contract_bindings_cover_inventory_surfaces() -> None:
    payload = build_gui_app_contract_bindings()

    assert payload["kind"] == GUI_APP_CONTRACT_BINDINGS_KIND
    assert payload["contract_count"] >= 8
    assert payload["summary"]["unresolved_contract_count"] == 0
    assert payload["summary"]["stable_unbound_contract_count"] == 0
    assert payload["summary"]["executes_media_operations_count"] == 0
    assert payload["readiness"]["ready"] is True

    contract_ids = {binding["contract_id"] for binding in payload["bindings"]}
    assert {"desktop_runtime", "people_review_bundle", "command_plan", "review_workbench_apply_preview", "review_workbench_confirmation_dialog", "review_workbench_apply_handoff_panel", "review_workbench_stateful_rebuild"} <= contract_ids


def test_gui_surface_registry_exposes_pages_panels_and_shell() -> None:
    surfaces = [surface.to_dict() for surface in list_gui_surface_bindings()]
    by_id = {surface["surface_id"]: surface for surface in surfaces}

    assert by_id["dashboard"]["surface_type"] == "page"
    assert by_id["desktop-shell"]["surface_type"] == "shell"
    assert by_id["review-workbench"]["surface_type"] == "page"
    assert by_id["people-review"]["page_id"] == "people-review"


def test_gui_app_contract_bindings_are_exposed_through_app_services() -> None:
    payload = build_via_app_services()

    assert payload["kind"] == GUI_APP_CONTRACT_BINDINGS_KIND
    assert payload["readiness"]["status"] == "ready"


def test_write_gui_app_contract_bindings_writes_json_file(tmp_path: Path) -> None:
    output = tmp_path / "contracts" / "gui_app_contract_bindings.json"

    payload = write_gui_app_contract_bindings(output)

    loaded = json.loads(output.read_text(encoding="utf-8"))
    assert loaded["kind"] == GUI_APP_CONTRACT_BINDINGS_KIND
    assert payload["written_file"] == str(output)


def test_contract_binding_summary_is_human_readable() -> None:
    summary = summarize_gui_app_contract_bindings(build_gui_app_contract_bindings())

    assert "GUI app-service contract bindings" in summary
    assert "Fully bound:" in summary
    assert "Ready: True" in summary


def test_cli_app_services_contract_bindings_json(tmp_path: Path, capsys) -> None:
    out = tmp_path / "bindings.json"

    assert app_services_main(["contract-bindings", "--json", "--out", str(out)]) == 0
    payload = json.loads(capsys.readouterr().out)
    written = json.loads(out.read_text(encoding="utf-8"))

    assert payload["kind"] == GUI_APP_CONTRACT_BINDINGS_KIND
    assert written["readiness"]["ready"] is True


def test_cli_app_services_contract_bindings_text(capsys) -> None:
    assert app_services_main(["contract-bindings"]) == 0

    text = capsys.readouterr().out
    assert "GUI app-service contract bindings" in text
    assert "Ready: True" in text


def test_desktop_runtime_includes_contract_binding_gate() -> None:
    state = build_gui_desktop_runtime_state(active_page_id="dashboard")

    assert state["app_contract_bindings"]["readiness"]["ready"] is True
    assert state["capabilities"]["app_contract_bindings_ready"] is True
    assert state["summary"]["app_contract_binding_status"] == "ready"
    assert any(check["id"] == "app-contract-bindings" and check["ok"] for check in state["readiness"]["checks"])


def test_desktop_runtime_out_dir_writes_contract_bindings(tmp_path: Path) -> None:
    payload = write_gui_desktop_runtime_state(tmp_path / "desktop", active_page_id="dashboard")

    assert payload["written_file_count"] == 19
    assert (tmp_path / "desktop" / "app_contract_bindings.json").exists()
    assert (tmp_path / "desktop" / "review_workbench_qt_widget_binding_plan.json").exists()
    assert (tmp_path / "desktop" / "review_workbench_interaction_plan.json").exists()
    assert (tmp_path / "desktop" / "review_workbench_apply_preview.json").exists()
    assert (tmp_path / "desktop" / "review_workbench_confirmation_dialog_model.json").exists()
    assert (tmp_path / "desktop" / "review_workbench_apply_executor_contract.json").exists()
    assert (tmp_path / "desktop" / "review_workbench_apply_executor_handoff_panel.json").exists()
    assert (tmp_path / "desktop" / "review_workbench_stateful_rebuild_loop.json").exists()
