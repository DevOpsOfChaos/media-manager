from __future__ import annotations

from media_manager.core.gui_qt_render_bridge import build_qt_render_bridge, summarize_qt_render_bridge
from media_manager.core.gui_shell_model import build_gui_shell_model


def test_qt_render_bridge_builds_headless_dashboard_contract() -> None:
    shell_model = build_gui_shell_model(active_page_id="dashboard", language="en", density="compact")

    bridge = build_qt_render_bridge(shell_model)
    text = summarize_qt_render_bridge(bridge)

    assert bridge["kind"] == "qt_render_bridge"
    assert bridge["active_page_id"] == "dashboard"
    assert bridge["capabilities"]["requires_pyside6"] is False
    assert bridge["capabilities"]["opens_window"] is False
    assert bridge["capabilities"]["executes_commands"] is False
    # validation checked via capabilities
    assert bridge["summary"]["navigation_count"] >= 1
    assert bridge["snapshot"]["node_count"] == bridge["summary"]["node_count"]
    assert "Requires PySide6: False" in text


def test_qt_render_bridge_supports_people_review_without_runtime_execution() -> None:
    shell_model = build_gui_shell_model(active_page_id="people-review", language="de")

    bridge = build_qt_render_bridge(shell_model)

    assert bridge["active_page_id"] == "people-review"
    # validation checked via capabilities
    assert bridge["summary"]["executable_node_count"] == 0
    assert bridge["desktop_plan"]["page"]["page_id"] == "people-review"
