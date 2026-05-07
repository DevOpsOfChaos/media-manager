from __future__ import annotations

import json
from pathlib import Path

from media_manager.cli_app_services import main as app_services_main
from media_manager.core.gui_qt_review_workbench_widget_bindings import (
    QT_REVIEW_WORKBENCH_WIDGET_BINDING_KIND,
    build_qt_review_workbench_widget_binding_plan,
    write_qt_review_workbench_widget_binding_plan,
)
from media_manager.core.gui_review_workbench_service import build_gui_review_workbench_service_bundle
from media_manager.core.gui_page_models import build_page_model
from media_manager.core.gui_qt_visible_page_adapter import build_qt_visible_page_plan


def test_widget_binding_plan_maps_adapter_components_to_qt_roles_without_importing_qt() -> None:
    service = build_gui_review_workbench_service_bundle(
        duplicate_review={"review_candidate_count": 2},
        people_review_summary={"group_count": 1, "face_count": 3},
        selected_lane_id="people-review",
    )
    plan = build_qt_review_workbench_widget_binding_plan(service["qt_adapter_package"])

    assert plan["kind"] == QT_REVIEW_WORKBENCH_WIDGET_BINDING_KIND
    assert plan["ready"] is True
    assert plan["capabilities"]["requires_pyside6"] is False
    assert plan["capabilities"]["opens_window"] is False
    assert plan["capabilities"]["executes_commands"] is False
    assert plan["summary"]["widget_binding_count"] == 4
    assert plan["summary"]["table_binding_count"] == 1
    assert plan["summary"]["sensitive_widget_count"] == 1

    by_role = {binding["role"]: binding for binding in plan["widget_bindings"]}
    assert by_role["toolbar"]["qt_widget_class"] == "QToolBar"
    assert by_role["filter_bar"]["qt_widget_class"] == "QWidget"
    assert by_role["review_lane_table"]["qt_widget_class"] == "QTableView"
    assert by_role["review_lane_table"]["qt_model_class"] == "QAbstractTableModel"
    assert by_role["lane_detail"]["privacy_mode"] == "local_redacted_preview"
    assert all(binding["executes_commands"] is False for binding in plan["widget_bindings"])


def test_review_workbench_service_embeds_widget_binding_plan() -> None:
    service = build_gui_review_workbench_service_bundle(duplicate_review={"review_candidate_count": 1})

    assert service["capabilities"]["qt_widget_binding_ready"] is True
    assert service["qt_widget_binding_plan"]["readiness"]["ready"] is True
    assert service["summary"]["qt_widget_binding_count"] == 4
    assert "review_workbench_qt_widget_binding_plan.json" in service["artifact_names"]


def test_visible_review_workbench_page_requires_widget_bindings() -> None:
    page = build_page_model("review-workbench", {})
    visible = build_qt_visible_page_plan(page)

    assert visible["body"]["kind"] == "qt_review_workbench_visible_plan"
    assert visible["body"]["ready_for_qt"] is True
    assert visible["body"]["summary"]["widget_binding_count"] == 4
    assert visible["body"]["summary"]["unbound_section_count"] == 0


def test_write_widget_binding_plan_writes_descriptor_only_payload(tmp_path: Path) -> None:
    service = build_gui_review_workbench_service_bundle(duplicate_review={"review_candidate_count": 1})
    payload = write_qt_review_workbench_widget_binding_plan(tmp_path / "bindings", service["qt_adapter_package"])

    assert payload["written_file_count"] == 2
    assert (tmp_path / "bindings" / "review_workbench_qt_widget_binding_plan.json").exists()
    assert (tmp_path / "bindings" / "README.txt").exists()
    loaded = json.loads((tmp_path / "bindings" / "review_workbench_qt_widget_binding_plan.json").read_text(encoding="utf-8"))
    assert loaded["kind"] == QT_REVIEW_WORKBENCH_WIDGET_BINDING_KIND
    assert loaded["readiness"]["ready"] is True


def test_cli_review_workbench_widget_bindings_json_and_out_dir(tmp_path: Path, capsys) -> None:
    assert app_services_main(["review-workbench-widget-bindings", "--json", "--selected-lane", "duplicates"]) == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["kind"] == QT_REVIEW_WORKBENCH_WIDGET_BINDING_KIND
    assert payload["readiness"]["ready"] is True
    assert payload["summary"]["widget_binding_count"] == 4

    out_dir = tmp_path / "widget-bindings"
    assert app_services_main(["review-workbench-widget-bindings", "--out-dir", str(out_dir)]) == 0
    text = capsys.readouterr().out
    assert "GUI Review Workbench Qt widget bindings" in text
    assert (out_dir / "review_workbench_qt_widget_binding_plan.json").exists()
