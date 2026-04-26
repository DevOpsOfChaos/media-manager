from __future__ import annotations

from media_manager.core.gui_onboarding import build_onboarding_state


def test_onboarding_is_localized() -> None:
    payload = build_onboarding_state(language="de")
    assert payload["title"] == "Willkommen im Media Manager"
    assert len(payload["steps"]) == 3
