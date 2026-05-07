from __future__ import annotations

import json
from pathlib import Path

from media_manager.cli_app_services import main as app_services_main
from media_manager.core.gui_review_workbench_interactions import (
    REVIEW_WORKBENCH_INTERACTION_KIND,
    build_review_workbench_interaction_intent,
    build_review_workbench_interaction_plan,
    write_review_workbench_interaction_plan,
)
from media_manager.core.gui_review_workbench_service import build_gui_review_workbench_service_bundle
from media_manager.core.gui_review_workbench_controller import reduce_review_workbench_state
from media_manager.core.gui_page_models import build_page_model
from media_manager.gui_review_workbench_qt import build_review_workbench_page_widget
from test_gui_qt_review_workbench_widget_skeleton_v1 import _FakeQtWidgets


def test_review_workbench_interaction_plan_wires_filter_table_toolbar_intents() -> None:
    service = build_gui_review_workbench_service_bundle(
        duplicate_review={"review_candidate_count": 2},
        people_review_summary={"group_count": 1, "face_count": 3},
        selected_lane_id="people-review",
        lane_query="people",
    )

    plan = build_review_workbench_interaction_plan(service)

    assert plan["kind"] == REVIEW_WORKBENCH_INTERACTION_KIND
    assert plan["ready"] is True
    assert plan["capabilities"]["executes_commands"] is False
    assert plan["summary"]["intent_count"] == 9
    assert plan["summary"]["signal_binding_count"] >= 7
    assert plan["summary"]["toolbar_binding_count"] == 4
    intent_kinds = {intent["intent_kind"] for intent in plan["intent_catalog"]}
    assert {
        "filter_query_changed",
        "filter_status_changed",
        "sort_mode_changed",
        "lane_selected",
        "table_row_activated",
        "toolbar_open_selected_lane",
        "toolbar_apply_reviewed_decisions",
    } <= intent_kinds
    apply_intent = next(intent for intent in plan["intent_catalog"] if intent["intent_kind"] == "toolbar_apply_reviewed_decisions")
    assert apply_intent["enabled"] is False
    assert apply_intent["executes_commands"] is False
    assert apply_intent["requires_explicit_user_confirmation"] is True


def test_interaction_intents_reduce_state_without_executing_commands() -> None:
    state = {
        "selected_lane_id": "duplicates",
        "lane_status_filter": "all",
        "lane_query": "",
        "lane_sort_mode": "attention_first",
        "page": 3,
        "page_size": 20,
    }
    query_intent = build_review_workbench_interaction_intent("filter_query_changed", query="people")
    reduced = reduce_review_workbench_state(state, query_intent)

    assert query_intent["action"] == "set_query"
    assert query_intent["executes_commands"] is False
    assert reduced["state"]["lane_query"] == "people"
    assert reduced["state"]["page"] == 1

    refresh_intent = build_review_workbench_interaction_intent("toolbar_refresh")
    refreshed = reduce_review_workbench_state(reduced["state"], refresh_intent)
    assert refreshed["changed"] is False
    assert refreshed["executes_commands"] is False


def test_review_workbench_service_embeds_interaction_plan() -> None:
    service = build_gui_review_workbench_service_bundle(duplicate_review={"review_candidate_count": 1})

    assert service["capabilities"]["qt_interaction_plan_ready"] is True
    assert service["interaction_plan"]["readiness"]["ready"] is True
    assert service["summary"]["interaction_intent_count"] == 9
    assert "review_workbench_interaction_plan.json" in service["artifact_names"]


def test_write_review_workbench_interaction_plan_outputs_plan_and_previews(tmp_path: Path) -> None:
    service = build_gui_review_workbench_service_bundle(duplicate_review={"review_candidate_count": 1})
    result = write_review_workbench_interaction_plan(tmp_path, service)

    assert result["written_file_count"] == 3
    assert (tmp_path / "review_workbench_interaction_plan.json").exists()
    assert (tmp_path / "review_workbench_interaction_state_previews.json").exists()
    loaded = json.loads((tmp_path / "review_workbench_interaction_plan.json").read_text(encoding="utf-8"))
    assert loaded["kind"] == REVIEW_WORKBENCH_INTERACTION_KIND


def test_cli_review_workbench_interactions_json_and_out_dir(tmp_path: Path, capsys) -> None:
    assert app_services_main(["review-workbench-interactions", "--json", "--selected-lane", "duplicates"]) == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["kind"] == REVIEW_WORKBENCH_INTERACTION_KIND
    assert payload["readiness"]["ready"] is True
    assert payload["summary"]["intent_count"] == 9

    out_dir = tmp_path / "interactions"
    assert app_services_main(["review-workbench-interactions", "--out-dir", str(out_dir)]) == 0
    text = capsys.readouterr().out
    assert "GUI Review Workbench interactions" in text
    assert (out_dir / "review_workbench_interaction_plan.json").exists()


def test_lazy_qt_builder_exposes_interaction_plan_and_action_intents() -> None:
    captured: list[dict[str, object]] = []
    page = build_page_model("review-workbench", {}, query="duplicate")

    mount = build_review_workbench_page_widget(_FakeQtWidgets, page, intent_dispatcher=captured.append)

    assert mount.interaction_plan["ready"] is True
    assert mount.interaction_plan["summary"]["intent_count"] == 9
    assert mount.model_sources["action_plan"]["capabilities"]["executes_commands"] is False
    open_action = mount.actions["open-selected-lane"]
    assert open_action.properties["intent_kind"] == "toolbar_open_selected_lane"
    assert open_action.properties["executes_commands"] is False
