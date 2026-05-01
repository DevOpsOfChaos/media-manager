from __future__ import annotations

from media_manager.core.app_contract_inventory import build_app_contract_inventory
from media_manager.core.gui_app_contract_bindings import build_gui_app_contract_bindings
from media_manager.core.gui_desktop_runtime_state import build_gui_desktop_runtime_state
from media_manager.core.gui_page_contracts import build_gui_navigation_state, build_gui_page_catalog
from media_manager.core.gui_page_models import build_page_model
from media_manager.core.gui_qt_visible_page_adapter import build_qt_visible_page_plan


def test_review_workbench_is_real_page_contract_and_navigation_target() -> None:
    catalog = build_gui_page_catalog()
    page_ids = {page["page_id"] for page in catalog["pages"]}
    assert "review-workbench" in page_ids

    navigation = build_gui_navigation_state("review-workbench")
    assert navigation["active_page_id"] == "review-workbench"
    assert any(item["page_id"] == "review-workbench" and item["active"] for item in navigation["items"])


def test_review_workbench_page_model_exposes_qt_adapter_payload() -> None:
    page = build_page_model("review-workbench", {}, query="duplicate")

    assert page["kind"] == "review_workbench_page"
    assert page["layout"] == "review_workbench_table_detail"
    assert page["qt_adapter_package"]["ready"] is True
    assert page["qt_widget_binding_plan"]["ready"] is True
    assert page["qt_widget_skeleton"]["ready"] is True
    assert page["table_model"]["kind"] == "ui_review_workbench_table_model"
    assert page["action_plan"]["capabilities"]["executes_commands"] is False

    visible = build_qt_visible_page_plan(page)
    assert visible["body"]["kind"] == "qt_review_workbench_visible_plan"
    assert visible["body"]["ready_for_qt"] is True
    assert visible["body"]["summary"]["component_count"] == 4
    assert visible["body"]["summary"]["widget_binding_count"] == 4


def test_desktop_runtime_can_open_review_workbench_page_headlessly() -> None:
    state = build_gui_desktop_runtime_state(active_page_id="review-workbench")

    assert state["readiness"]["ready"] is True
    assert state["summary"]["active_page_id"] == "review-workbench"
    assert state["summary"]["page_kind"] == "review_workbench_page"
    assert state["summary"]["visible_body_kind"] == "qt_review_workbench_visible_plan"
    assert state["summary"]["review_workbench_qt_component_count"] == 4
    assert state["summary"]["review_workbench_qt_widget_binding_count"] == 4
    assert state["summary"]["review_workbench_qt_widget_skeleton_node_count"] == 4
    assert state["capabilities"]["review_workbench_adapter_ready"] is True
    assert state["capabilities"]["review_workbench_widget_bindings_ready"] is True
    assert state["capabilities"]["review_workbench_widget_skeleton_ready"] is True
    assert state["review_workbench_service"]["readiness"]["ready"] is True


def test_contract_inventory_and_bindings_include_review_workbench_service() -> None:
    inventory = build_app_contract_inventory()
    contract_ids = {contract["contract_id"] for contract in inventory["contracts"]}
    assert "review_workbench_service" in contract_ids

    bindings = build_gui_app_contract_bindings()
    assert bindings["readiness"]["ready"] is True
    review_binding = next(binding for binding in bindings["bindings"] if binding["contract_id"] == "review_workbench_service")
    assert review_binding["fully_bound"] is True
    assert any(surface["surface_id"] == "review-workbench" for surface in review_binding["bound_surfaces"])
