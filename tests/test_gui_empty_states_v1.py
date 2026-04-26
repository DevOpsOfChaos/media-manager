from __future__ import annotations

from media_manager.core.gui_empty_states import build_empty_state


def test_people_empty_state_is_localized() -> None:
    state = build_empty_state("people-review", language="de")

    assert "Personen" in state["title"] or "Öffne" in state["title"]
    assert state["page_id"] == "people-review"
