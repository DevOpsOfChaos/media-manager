from __future__ import annotations

from media_manager.core.gui_qt_render_tree import build_leaf_node, build_render_node
from media_manager.core.gui_qt_runtime_plan_validator import validate_qt_runtime_widget_plan
from media_manager.core.gui_qt_runtime_widget_plan import build_qt_runtime_widget_plan, collect_runtime_widget_ids


def test_runtime_widget_plan_maps_render_tree_without_qt_imports() -> None:
    root = build_render_node(
        "shell",
        "ShellFrame",
        role="application_shell",
        children=[
            build_leaf_node("nav-dashboard", "NavigationItem", role="navigation_item", props={"label": "Dashboard"}),
            build_leaf_node("status", "StatusBar", role="status", props={"text": "Ready"}),
        ],
    )

    plan = build_qt_runtime_widget_plan(root)

    assert plan["capabilities"]["requires_pyside6"] is False
    assert plan["capabilities"]["opens_window"] is False
    assert plan["root"]["qt_widget"] == "QWidget"
    assert plan["root"]["children"][0]["qt_widget"] == "QPushButton"
    assert "nav-dashboard" in collect_runtime_widget_ids(plan)
    assert validate_qt_runtime_widget_plan(plan)["valid"] is True


def test_runtime_widget_plan_preserves_sensitive_flags_and_defers_execution() -> None:
    root = build_render_node(
        "people-root",
        "PeopleReviewPage",
        children=[
            build_leaf_node("face-1", "FaceCard", role="people_face", props={"face_id": "face-1"}, sensitive=True),
            build_render_node("apply", "Button", role="action", executes_immediately=True),
        ],
    )

    plan = build_qt_runtime_widget_plan(root)
    validation = validate_qt_runtime_widget_plan(plan)

    assert plan["summary"]["sensitive_node_count"] == 1
    assert plan["summary"]["deferred_execution_count"] == 1
    assert validation["valid"] is True
    assert validation["warning_count"] >= 1
