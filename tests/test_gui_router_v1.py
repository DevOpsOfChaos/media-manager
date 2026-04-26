from __future__ import annotations

from media_manager.core.gui_router import build_gui_router_state, normalize_route


def test_normalize_route_aliases() -> None:
    assert normalize_route("runs") == "run-history"
    assert normalize_route("people") == "people-review"
    assert normalize_route("doctor") == "settings"


def test_build_gui_router_state_marks_active_route() -> None:
    state = build_gui_router_state(active_page_id="people", language="de")

    assert state["active_page_id"] == "people-review"
    active = [item for item in state["routes"] if item["active"]]
    assert len(active) == 1
    assert active[0]["page_id"] == "people-review"
    assert active[0]["label"] == "Personenprüfung"
