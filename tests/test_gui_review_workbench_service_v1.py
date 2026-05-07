from __future__ import annotations

import json
from pathlib import Path

from media_manager.core.gui_review_workbench_service import (
    build_gui_review_workbench_service_bundle,
    write_gui_review_workbench_service_bundle,
)
from media_manager.core.gui_qt_review_workbench_adapter import build_qt_review_workbench_adapter_package


def test_review_workbench_service_builds_qt_ready_bundle_without_execution() -> None:
    payload = build_gui_review_workbench_service_bundle(
        duplicate_review={"review_candidate_count": 3, "run_count": 1},
        similar_images={"review_candidate_count": 1},
        decision_summary={"error_count": 0, "review_candidate_count": 0},
        people_review_summary={"group_count": 2, "face_count": 5},
        selected_lane_id="people-review",
        lane_status_filter="needs_review",
        lane_sort_mode="attention_first",
    )

    assert payload["kind"] == "gui_review_workbench_service_bundle"
    assert payload["readiness"]["ready"] is True
    assert payload["summary"]["lane_count"] == 7
    assert payload["summary"]["attention_count"] == 7
    assert payload["summary"]["selected_lane_id"] == "people-review"
    assert payload["capabilities"]["requires_pyside6"] is False
    assert payload["capabilities"]["opens_window"] is False
    assert payload["capabilities"]["executes_commands"] is False
    assert payload["capabilities"]["apply_enabled"] is False
    assert payload["apply_preview"]["capabilities"]["executes_commands"] is False
    assert payload["confirmation_dialog"]["capabilities"]["executes_commands"] is False
    assert payload["apply_executor_contract"]["capabilities"]["executes_commands"] is False
    assert payload["executor_handoff_panel"]["capabilities"]["executes_commands"] is False

    adapter = payload["qt_adapter_package"]
    assert adapter["kind"] == "qt_review_workbench_adapter_package"
    assert adapter["ready"] is True
    assert adapter["summary"]["component_count"] == 4
    assert any(component["component_type"] == "ReviewWorkbenchTable" for component in adapter["components"])
    assert all(component["executes_commands"] is False for component in adapter["components"])

    widget_plan = payload["qt_widget_binding_plan"]
    assert widget_plan["ready"] is True
    assert widget_plan["summary"]["widget_binding_count"] == 4
    assert widget_plan["capabilities"]["executes_commands"] is False

    interactions = payload["interaction_plan"]
    assert interactions["ready"] is True
    assert interactions["summary"]["intent_count"] >= 8
    assert interactions["capabilities"]["executes_commands"] is False


def test_review_workbench_service_reads_people_bundle_summary(tmp_path: Path) -> None:
    bundle = tmp_path / "people_bundle"
    bundle.mkdir()
    (bundle / "bundle_manifest.json").write_text(
        json.dumps({"status": "ok", "summary": {"group_count": 2, "face_count": 4}}),
        encoding="utf-8",
    )
    (bundle / "people_review_workspace.json").write_text(json.dumps({"groups": [{"group_id": "g1"}, {"group_id": "g2"}]}), encoding="utf-8")
    (bundle / "people_review_workflow.json").write_text(json.dumps({"workflow": "people_review"}), encoding="utf-8")

    payload = build_gui_review_workbench_service_bundle(people_bundle_dir=bundle, selected_lane_id="people-review")

    assert payload["inputs"]["people_bundle_dir"] == str(bundle)
    assert payload["view_model"]["selected_lane_id"] == "people-review"
    assert payload["summary"]["attention_count"] == 2


def test_review_workbench_service_writes_split_artifacts(tmp_path: Path) -> None:
    result = write_gui_review_workbench_service_bundle(
        tmp_path,
        duplicate_review={"review_candidate_count": 1},
        selected_lane_id="duplicates",
    )

    assert result["written_file_count"] == 18
    assert (tmp_path / "review_workbench_service_bundle.json").exists()
    assert (tmp_path / "review_workbench_qt_adapter_package.json").exists()
    assert (tmp_path / "review_workbench_qt_widget_binding_plan.json").exists()
    assert (tmp_path / "review_workbench_qt_widget_skeleton.json").exists()
    assert (tmp_path / "review_workbench_interaction_plan.json").exists()
    assert (tmp_path / "review_workbench_callback_mount_plan.json").exists()
    assert (tmp_path / "review_workbench_apply_preview.json").exists()
    assert (tmp_path / "review_workbench_confirmation_dialog_model.json").exists()
    assert (tmp_path / "review_workbench_apply_executor_contract.json").exists()
    assert (tmp_path / "review_workbench_apply_executor_handoff_panel.json").exists()
    assert (tmp_path / "README.txt").exists()
    written = json.loads((tmp_path / "review_workbench_service_bundle.json").read_text(encoding="utf-8"))
    assert written["summary"]["selected_lane_id"] == "duplicates"


def test_qt_adapter_package_keeps_navigation_as_route_intents() -> None:
    service = build_gui_review_workbench_service_bundle(
        duplicate_review={"review_candidate_count": 2},
        selected_lane_id="duplicates",
    )
    adapter = build_qt_review_workbench_adapter_package(
        view_model=service["view_model"],
        table_model=service["table_model"],
        action_plan=service["action_plan"],
        controller_state=service["controller_state"],
        qt_workbench=service["qt_workbench"],
    )

    assert adapter["readiness"]["ready"] is True
    assert adapter["capabilities"]["executes_commands"] is False
    assert adapter["route_intents"]
    assert any(intent["target_page_id"] == "run-history" for intent in adapter["route_intents"])
    assert all(intent["executes_commands"] is False for intent in adapter["route_intents"])
