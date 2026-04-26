from media_manager.core.gui_qt_demo_workspace import build_demo_people_page
from media_manager.core.gui_qt_inspector_panel import build_inspector_panel, summarize_inspector_panel
from media_manager.core.gui_qt_review_focus_mode import build_focus_toolbar, build_review_focus_mode
from media_manager.core.gui_qt_visual_density_tuner import build_density_options, build_density_tuning


def test_focus_mode_and_toolbar_are_non_executing() -> None:
    page = build_demo_people_page()
    focus = build_review_focus_mode(page, selected_group_id="unknown-1")
    assert focus["enabled"] is True
    toolbar = build_focus_toolbar(focus)
    assert toolbar["action_count"] == 3
    assert all(action["executes_immediately"] is False for action in toolbar["actions"])


def test_density_and_inspector_models() -> None:
    density = build_density_tuning("spacious", page_id="people-review")
    assert density["density"] == "spacious"
    assert density["tokens"]["face_card_size"] > 160
    assert build_density_options()["default"] == "comfortable"
    panel = build_inspector_panel({"page": {"title": "x"}})
    assert summarize_inspector_panel(panel)["has_tree"] is True
