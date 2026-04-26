from media_manager.core.gui_qt_navigation_rail import build_navigation_rail
from media_manager.core.gui_qt_top_bar_model import build_top_bar_model
from media_manager.core.gui_qt_safety_banner import build_safety_banner
from media_manager.core.gui_qt_drawer_stack import build_drawer_stack
from media_manager.core.gui_qt_page_slots import build_page_slots
from media_manager.core.gui_qt_app_frame_model import build_app_frame_model, summarize_app_frame
from media_manager.core.gui_qt_view_handoff import build_qt_view_handoff, validate_qt_view_handoff


def _shell(page=None):
    page = page or {"page_id": "dashboard", "kind": "dashboard_page", "title": "Dashboard", "hero": {}, "cards": [{"title": "A"}]}
    return {
        "application": {"title": "Media Manager"},
        "active_page_id": page["page_id"],
        "language": "de",
        "theme": {"theme": "modern-dark", "palette": {"accent": "#60a5fa"}},
        "window": {"width": 1400, "height": 900},
        "navigation": [
            {"id": "dashboard", "label": "Übersicht", "icon": "home"},
            {"id": "people-review", "label": "Personen", "icon": "users"},
        ],
        "page": page,
        "status_bar": {"privacy": "Personendaten bleiben lokal."},
        "onboarding": {"dismissed": True},
    }


def test_navigation_rail_marks_active_and_shortcuts() -> None:
    rail = build_navigation_rail([{"id": "dashboard", "label": "Dash"}, {"id": "people", "label": "People"}], active_page_id="people")
    assert rail["active_page_id"] == "people-review"
    assert rail["items"][1]["active"] is True
    assert rail["items"][0]["shortcut"] == "Ctrl+1"


def test_top_bar_and_safety_banner_are_page_aware() -> None:
    shell = _shell({"page_id": "people-review", "kind": "people_review_page", "title": "People", "asset_refs": [{"path": "face.jpg"}]})
    top = build_top_bar_model(shell)
    banner = build_safety_banner(shell)
    assert top["page_title"] == "People"
    assert top["action_count"] >= 2
    assert banner["visible"] is True
    assert banner["severity"] == "warning"


def test_drawer_stack_counts_attention() -> None:
    stack = build_drawer_stack({"notifications": {"message_count": 2, "error_count": 1}, "onboarding": {"dismissed": False, "steps": [1, 2]}})
    assert stack["drawer_count"] == 4
    assert stack["open_drawer_count"] == 1
    assert stack["attention_count"] >= 1


def test_page_slots_detect_dashboard_and_people() -> None:
    dash = build_page_slots({"page_id": "dashboard", "kind": "dashboard_page", "title": "Dashboard", "hero": {}, "cards": [{}]})
    people = build_page_slots({"page_id": "people-review", "kind": "people_review_page", "title": "People", "queue": {}, "detail": {}})
    assert dash["ready"] is True
    assert people["ready"] is True


def test_app_frame_and_handoff_are_valid() -> None:
    shell = _shell()
    frame = build_app_frame_model(shell)
    summary = summarize_app_frame(frame)
    handoff = build_qt_view_handoff(shell)
    assert frame["ready"] is True
    assert summary["navigation_items"] == 2
    assert validate_qt_view_handoff(handoff)["valid"] is True
    assert handoff["handoff_contract"]["executes_commands"] is False
