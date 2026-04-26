from media_manager.core.gui_qt_view_action_registry import build_view_action_registry, normalize_view_action


def test_action_registry_normalizes_navigation_and_safety() -> None:
    registry = build_view_action_registry(
        page_actions=[{"id": "apply_ready", "label": "Apply", "risk_level": "high"}],
        navigation=[{"id": "dashboard", "label": "Dashboard", "shortcut": "Ctrl+1"}],
    )

    assert registry["action_count"] == 2
    assert registry["confirmation_count"] == 1
    assert registry["executes_immediately"] is False


def test_normalize_action_is_non_executing() -> None:
    row = normalize_view_action({"id": "open", "enabled": False}, source="test")
    assert row["id"] == "open"
    assert row["enabled"] is False
    assert row["executes_immediately"] is False
