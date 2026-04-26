from media_manager.core.gui_qt_context_menu import build_qt_context_menu
from media_manager.core.gui_qt_drop_zone import build_drop_zone, classify_dropped_paths


def test_people_context_menu_contains_safe_confirmation_actions() -> None:
    menu = build_qt_context_menu("face_card", {"face_id": "face-1"}, language="en")

    assert menu["item_count"] == 2
    assert menu["confirmation_count"] == 1
    assert menu["executes_immediately"] is False


def test_drop_zone_classifies_files_and_rejections() -> None:
    zone = build_drop_zone("people_bundle", accepts_directories=False)
    result = classify_dropped_paths(["bundle.json", "photo.jpg"], zone)

    assert result["accepted_count"] == 1
    assert result["rejected_count"] == 1
