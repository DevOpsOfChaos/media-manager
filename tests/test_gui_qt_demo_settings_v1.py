from media_manager.core.gui_qt_demo_workspace import build_demo_workspace_bundle
from media_manager.core.gui_qt_settings_workspace import build_settings_workspace, validate_settings_workspace


def test_demo_workspace_has_people_review_shell() -> None:
    bundle = build_demo_workspace_bundle()
    assert bundle["shell_model"]["active_page_id"] == "people-review"
    assert bundle["people_page"]["groups"]
    assert bundle["home_state"]["people_review"]["ready_for_gui"] is True


def test_settings_workspace_validates_privacy_warning() -> None:
    workspace = build_settings_workspace({"language": "de", "theme": "modern-light"})
    assert workspace["field_count"] == 5
    validation = validate_settings_workspace(workspace)
    assert validation["valid"] is True
    assert "people_privacy_not_acknowledged" in validation["warnings"]
