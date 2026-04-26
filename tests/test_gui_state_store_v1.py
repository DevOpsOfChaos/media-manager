from __future__ import annotations

from pathlib import Path

from media_manager.core.gui_state_store import (
    add_recent_path,
    build_default_gui_state,
    build_gui_state_summary,
    load_gui_state,
    register_people_bundle,
    set_active_page,
    write_gui_state,
)


def test_gui_state_round_trip_and_recent_paths(tmp_path: Path) -> None:
    state_path = tmp_path / "gui_state.json"
    state = build_default_gui_state(workspace_root=tmp_path)
    state = add_recent_path(state, section="run_dirs", path=tmp_path / "runs")
    state = add_recent_path(state, section="run_dirs", path=tmp_path / "runs")
    state = set_active_page(state, "people-review")
    write_gui_state(state_path, state)

    loaded = load_gui_state(state_path)
    summary = build_gui_state_summary(loaded)

    assert loaded["active_page_id"] == "people-review"
    assert loaded["recent"]["run_dirs"] == [str(tmp_path / "runs")]
    assert summary["recent_counts"]["run_dirs"] == 1


def test_register_people_bundle_sets_active_page_and_catalog(tmp_path: Path) -> None:
    state = build_default_gui_state()
    bundle_dir = tmp_path / "bundle"
    catalog_path = tmp_path / "people.json"

    updated = register_people_bundle(state, bundle_dir=bundle_dir, catalog_path=catalog_path)

    assert updated["active_page_id"] == "people-review"
    assert updated["people_review"]["last_bundle_dir"] == str(bundle_dir)
    assert updated["people_review"]["last_catalog_path"] == str(catalog_path)
    assert updated["recent"]["people_bundle_dirs"] == [str(bundle_dir)]
    assert updated["recent"]["catalog_paths"] == [str(catalog_path)]
