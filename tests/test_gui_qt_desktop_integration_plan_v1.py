from __future__ import annotations

from media_manager.core.gui_qt_desktop_integration_plan import (
    build_qt_desktop_integration_plan,
    summarize_qt_desktop_integration_plan,
)
from media_manager.core.gui_shell_model import build_gui_shell_model


def test_desktop_integration_plan_builds_dashboard_runtime_plan_headlessly() -> None:
    shell = build_gui_shell_model(active_page_id="dashboard", language="en")

    plan = build_qt_desktop_integration_plan(shell)

    assert plan["kind"] == "qt_desktop_integration_plan"
    assert plan["active_page_id"] == "dashboard"
    assert plan["capabilities"]["requires_pyside6"] is False
    assert plan["capabilities"]["opens_window"] is False
    assert plan["runtime_validation"]["valid"] is True
    assert plan["summary"]["runtime_node_count"] >= 3


def test_desktop_integration_plan_marks_people_review_as_sensitive_local_only() -> None:
    shell = build_gui_shell_model(
        active_page_id="people-review",
        home_state={
            "pages": [{"id": "people-review", "label": "People Review"}],
            "people_review": {
                "groups": [
                    {
                        "group_id": "person-1",
                        "display_label": "Unknown person",
                        "status": "needs_review",
                        "face_count": 1,
                    }
                ],
                "selected_group_id": "person-1",
                "detail": {
                    "title": "Unknown person",
                    "faces": [
                        {
                            "face_id": "face-1",
                            "path": "faces/face-1.jpg",
                            "decision_status": "pending",
                            "asset_ref": {"path": "faces/face-1.jpg"},
                        }
                    ],
                },
            },
        },
    )

    plan = build_qt_desktop_integration_plan(shell)

    assert plan["active_page_id"] == "people-review"
    assert plan["capabilities"]["local_only"] is True
    assert plan["summary"]["sensitive_node_count"] >= 1
    assert plan["summary"]["deferred_execution_count"] == 0


def test_summarize_desktop_integration_plan_mentions_runtime_nodes() -> None:
    plan = build_qt_desktop_integration_plan(build_gui_shell_model(active_page_id="dashboard"))

    text = summarize_qt_desktop_integration_plan(plan)

    assert "Qt desktop integration plan" in text
    assert "Runtime nodes:" in text
    assert "Requires PySide6: False" in text
