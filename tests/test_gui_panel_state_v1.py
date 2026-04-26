from __future__ import annotations

from media_manager.core.gui_panel_state import normalize_panel_state, update_panel_size, update_panel_visibility


def test_panel_state_normalizes_defaults_and_clamps() -> None:
    state = normalize_panel_state({"sidebar": {"width": 9999}, "detail": {"visible": False}})

    assert state["panels"]["sidebar"]["width"] == 420
    assert state["panels"]["detail"]["visible"] is False
    assert state["visible_panel_count"] == 2


def test_panel_updates_are_stable() -> None:
    state = update_panel_visibility(None, panel_id="activity", visible=False)
    assert state["panels"]["activity"]["visible"] is False

    resized = update_panel_size(state["panels"], panel_id="detail", size=100)
    assert resized["panels"]["detail"]["width"] == 320
