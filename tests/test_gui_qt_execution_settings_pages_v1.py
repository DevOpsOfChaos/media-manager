from __future__ import annotations

from media_manager.core.gui_qt_execution_page import build_qt_execution_page_plan
from media_manager.core.gui_qt_settings_page import build_qt_settings_page_plan


def test_execution_page_plan_is_safe_and_complete() -> None:
    plan = build_qt_execution_page_plan({"monitor": {"status": "queued"}, "queue": {"jobs": [{"id": "job-1"}]}})

    assert plan["status"] == "queued"
    assert {item["widget_type"] for item in plan["widgets"]} == {"execution_monitor", "command_queue", "log_stream", "job_history"}


def test_settings_page_plan_builds_sections() -> None:
    plan = build_qt_settings_page_plan({"sections": [{"id": "appearance", "title": "Appearance", "items": [{"label": "Theme", "value": "dark"}]}]})

    assert plan["layout"] == "settings_sections"
    assert plan["widgets"][0]["widget_type"] == "settings_section"
    assert plan["widgets"][0]["items"][0]["label"] == "Theme"
