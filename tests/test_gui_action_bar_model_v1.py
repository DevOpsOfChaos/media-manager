from media_manager.core.gui_action_bar_model import build_action_bar, recommended_action


def test_action_bar_buckets_actions() -> None:
    bar = build_action_bar([
        {"id": "preview", "label": "Preview", "recommended": True},
        {"id": "apply", "label": "Apply", "risk_level": "high", "requires_confirmation": True},
        {"id": "blocked", "label": "Blocked", "enabled": False},
    ])
    assert bar["enabled_count"] == 2
    assert bar["confirmation_count"] == 1
    assert bar["buckets"]["danger"][0]["id"] == "apply"
    assert recommended_action(bar)["id"] == "preview"
