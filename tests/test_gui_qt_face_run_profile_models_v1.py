from media_manager.core.gui_qt_people_face_strip import build_people_face_strip, build_people_face_strip_from_page
from media_manager.core.gui_qt_run_cards import build_run_cards
from media_manager.core.gui_qt_profile_cards import build_profile_cards


def test_people_face_strip_marks_sensitive_and_selected() -> None:
    strip = build_people_face_strip([
        {"face_id": "f1", "path": "a.jpg", "include": True},
        {"face_id": "f2", "path": "b.jpg", "include": False},
    ], selected_face_id="f2")
    assert strip["sensitive"] is True
    assert strip["face_count"] == 2
    assert strip["items"][1]["selected"] is True
    assert strip["items"][1]["status"] == "excluded"


def test_people_face_strip_from_page_falls_back_to_asset_refs() -> None:
    strip = build_people_face_strip_from_page({"detail": {}, "asset_refs": [{"face_id": "asset-1", "path": "crop.jpg"}]})
    assert strip["face_count"] == 1
    assert strip["items"][0]["thumbnail_role"] == "face_crop"


def test_run_cards_detect_attention() -> None:
    cards = build_run_cards([
        {"run_id": "r1", "command": "people", "exit_code": 0},
        {"run_id": "r2", "command": "duplicates", "exit_code": 1},
    ])
    assert cards["card_count"] == 2
    assert cards["attention_count"] == 1
    assert cards["cards"][1]["status"] == "attention"


def test_profile_cards_count_favorites_and_invalid() -> None:
    cards = build_profile_cards([
        {"profile_id": "p1", "title": "People", "favorite": True, "valid": True},
        {"profile_id": "p2", "title": "Broken", "valid": False},
    ])
    assert cards["favorite_count"] == 1
    assert cards["invalid_count"] == 1
    assert cards["cards"][0]["status"] == "ready"
