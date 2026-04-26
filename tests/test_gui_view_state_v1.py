from __future__ import annotations

from pathlib import Path

from media_manager.core.gui_view_state import normalize_gui_view_state, update_gui_view_state, write_gui_view_state, load_gui_view_state


def test_normalize_gui_view_state_aliases_and_defaults() -> None:
    state = normalize_gui_view_state({"active_page_id": "people", "recent_pages": ["people", "people", "dashboard"]})

    assert state["active_page_id"] == "people-review"
    assert state["recent_pages"] == ["people", "dashboard"]
    assert state["run_filter"] == "all"


def test_update_gui_view_state_tracks_recent_pages_and_bundles() -> None:
    state = update_gui_view_state({}, active_page_id="runs", people_bundle_dir="bundle-a", search_query="max")

    assert state["active_page_id"] == "run-history"
    assert state["recent_pages"] == ["run-history"]
    assert state["recent_bundles"] == ["bundle-a"]
    assert state["search_query"] == "max"


def test_write_and_load_gui_view_state(tmp_path: Path) -> None:
    path = tmp_path / "view.json"
    write_gui_view_state(path, {"active_page_id": "new run"})

    loaded = load_gui_view_state(path)

    assert loaded["active_page_id"] == "new-run"
