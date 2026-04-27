from __future__ import annotations


def sample_visible_surface(*, unsupported: bool = False) -> dict[str, object]:
    action_component = "UnsupportedActions" if unsupported else "ActionBar"
    return {
        "kind": "qt_runtime_smoke_visible_surface",
        "page_id": "runtime-smoke",
        "active_page_id": "people-review",
        "visible_plan": {
            "kind": "qt_runtime_smoke_visible_plan",
            "page_id": "runtime-smoke",
            "title": "Runtime Smoke",
            "subtitle": "Review Qt runtime readiness before opening a window.",
            "summary": {
                "section_count": 4,
                "row_count": 2,
                "action_count": 2,
                "ready_for_runtime_review": True,
                "contains_sensitive_people_data_possible": True,
                "local_only": True,
            },
            "sections": [
                {"id": "runtime-smoke-status", "title": "Runtime smoke status", "component": "StatusBanner", "props": {"severity": "success", "ready": True}, "items": []},
                {"id": "runtime-smoke-table", "title": "Runtime smoke metrics", "component": "DataTable", "props": {"row_count": 2}, "items": [{"row_id": "current-report", "title": "Current", "ready": True}, {"row_id": "artifacts", "title": "Artifacts", "ready": False}]},
                {"id": "runtime-smoke-detail", "title": "Runtime smoke detail", "component": "DetailPanel", "props": {"local_only": True, "contains_sensitive_people_data_possible": True}, "items": []},
                {"id": "runtime-smoke-actions", "title": "Runtime smoke actions", "component": action_component, "props": {"action_count": 2}, "items": [{"id": "refresh-runtime-smoke", "label": "Refresh", "enabled": True}, {"id": "start-manual-qt-smoke", "label": "Start", "enabled": True, "requires_confirmation": True}]},
            ],
        },
        "layout_plan": {
            "kind": "qt_runtime_smoke_layout_plan",
            "placements": [
                {"section_id": "runtime-smoke-status", "row": 0, "column": 0, "column_span": 2},
                {"section_id": "runtime-smoke-table", "row": 1, "column": 0, "column_span": 1},
                {"section_id": "runtime-smoke-detail", "row": 1, "column": 1, "column_span": 1},
                {"section_id": "runtime-smoke-actions", "row": 2, "column": 0, "column_span": 2},
            ],
        },
        "summary": {
            "section_count": 4,
            "placement_count": 4,
            "label_count": 5,
            "ready_for_runtime_review": True,
            "has_privacy_notice": True,
            "ready_for_qt_adapter": True,
            "local_only": True,
        },
        "capabilities": {"requires_pyside6": False, "opens_window": False, "headless_testable": True, "executes_commands": False, "local_only": True},
        "ready_for_qt_adapter": True,
    }

from media_manager.core.gui_qt_runtime_smoke_render_plan import build_qt_runtime_smoke_render_plan
from media_manager.core.gui_qt_runtime_smoke_widget_tree import build_qt_runtime_smoke_widget_tree


def test_render_plan_orders_tree_nodes_without_execution() -> None:
    surface = sample_visible_surface()
    tree = build_qt_runtime_smoke_widget_tree(surface)
    render = build_qt_runtime_smoke_render_plan(tree, surface["layout_plan"])
    assert render["summary"]["render_step_count"] == tree["summary"]["node_count"]
    assert render["summary"]["executable_step_count"] == 0
    assert render["summary"]["placed_step_count"] == 4
    assert render["steps"][0]["node_id"] == "runtime-smoke-root"
