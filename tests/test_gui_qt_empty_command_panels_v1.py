from media_manager.core.gui_qt_command_preview_panel import build_qt_command_preview_panel
from media_manager.core.gui_qt_empty_state_renderer import build_qt_empty_state_render_plan


def test_empty_state_plan_uses_default_title() -> None:
    plan = build_qt_empty_state_render_plan(None, page_id="people-review")
    assert plan["visible"] is True
    assert plan["widget"] == "empty_state"


def test_command_preview_flags_risky_args() -> None:
    panel = build_qt_command_preview_panel(["media-manager", "duplicates", "--apply", "--yes"])
    assert panel["requires_confirmation"] is True
    assert panel["executes_immediately"] is False
    assert "--apply" in panel["risky_flags"]
