from media_manager.core.gui_qt_localization_audit import audit_qt_localization


def test_localization_audit_flags_english_markers_for_german() -> None:
    audit = audit_qt_localization({"title": "Dashboard", "nested": {"label": "Bereit"}}, language="de")
    assert audit["ok"] is False
    assert audit["possible_english_count"] == 1


def test_localization_audit_accepts_german_text() -> None:
    assert audit_qt_localization({"title": "Übersicht"}, language="de")["ok"] is True
