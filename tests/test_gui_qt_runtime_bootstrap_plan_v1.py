from __future__ import annotations

from media_manager.core.gui_qt_runtime_bootstrap_plan import build_qt_runtime_bootstrap_plan


def test_runtime_bootstrap_plan_wraps_build_steps_validation_and_snapshot() -> None:
    desktop_plan = {
        "kind": "qt_desktop_integration_plan",
        "active_page_id": "dashboard",
        "ready": True,
        "summary": {"active_page_id": "dashboard"},
        "runtime_widget_plan": {
            "root": {
                "id": "shell",
                "source_component": "ShellFrame",
                "supported_component": True,
                "qt_widget": "QWidget",
                "layout": "QHBoxLayout",
                "props": {"title": "Media Manager"},
                "children": [],
                "sensitive": False,
                "execute_policy": "none",
            }
        },
    }

    bootstrap = build_qt_runtime_bootstrap_plan(desktop_plan)

    assert bootstrap["kind"] == "qt_runtime_bootstrap_plan"
    assert bootstrap["ready"] is True
    assert bootstrap["validation"]["valid"] is True
    assert bootstrap["snapshot"]["payload_hash"]
    assert bootstrap["summary"]["build_step_count"] >= 2
    assert bootstrap["capabilities"]["requires_pyside6"] is False
    assert bootstrap["capabilities"]["opens_window"] is False
