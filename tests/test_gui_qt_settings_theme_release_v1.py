from media_manager.core.gui_qt_settings_apply_plan import build_settings_apply_plan
from media_manager.core.gui_qt_theme_preview import build_theme_preview
from media_manager.core.gui_qt_release_gate import build_release_gate


def test_settings_apply_plan_detects_refresh_and_sensitive_changes() -> None:
    plan = build_settings_apply_plan({"language": "en", "people_privacy_acknowledged": False}, {"language": "de", "people_privacy_acknowledged": True})
    assert plan["change_count"] == 2
    assert plan["requires_ui_refresh"] is True
    assert plan["sensitive_change_count"] == 1
    assert plan["executes_immediately"] is False


def test_theme_preview_accepts_palette_or_tokens() -> None:
    preview = build_theme_preview({"theme": "modern-light", "tokens": {"background": "#fff", "surface": "#eee", "text": "#111", "accent": "#00f"}})
    assert preview["has_required_colors"] is True
    assert preview["chip_count"] == 4
    assert preview["sample_cards"][0]["accent"] == "#00f"


def test_release_gate_blocks_on_error_checks() -> None:
    gate = build_release_gate([{"id": "tests", "passed": True}, {"id": "qt", "status": "failed", "message": "missing"}])
    assert gate["ready"] is False
    assert gate["error_count"] == 1
