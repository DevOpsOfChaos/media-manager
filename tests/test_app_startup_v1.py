from __future__ import annotations

import json
from pathlib import Path

from media_manager.core.app_startup import build_app_startup_state
from media_manager.core.gui_state_store import build_default_gui_state, register_people_bundle, write_gui_state


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def _write_minimal_bundle(bundle: Path) -> None:
    _write_json(bundle / "bundle_manifest.json", {"status": "ok", "summary": {"ready_group_count": 0}})
    _write_json(bundle / "people_report.json", {"schema_version": 1})
    _write_json(bundle / "people_review_workflow.json", {"workflow": "people_review"})
    _write_json(bundle / "people_review_workspace.json", {"workspace": "people_review_workspace"})
    (bundle / "summary.txt").write_text("summary", encoding="utf-8")
    _write_json(bundle / "assets" / "people_review_assets.json", {"assets": []})


def test_startup_state_loads_gui_state_and_validates_people_bundle(tmp_path: Path) -> None:
    bundle = tmp_path / "bundle"
    _write_minimal_bundle(bundle)
    state = register_people_bundle(build_default_gui_state(), bundle_dir=bundle)
    state_path = tmp_path / "gui_state.json"
    write_gui_state(state_path, state)

    startup = build_app_startup_state(gui_state_path=state_path)

    assert startup["kind"] == "app_startup_state"
    assert startup["active_page_id"] == "people-review"
    assert startup["gui_state_loaded"] is True
    assert startup["people_bundle_validation"]["ready_for_gui"] is True


def test_startup_state_is_safe_without_existing_state(tmp_path: Path) -> None:
    startup = build_app_startup_state(gui_state_path=tmp_path / "missing.json")

    assert startup["gui_state_loaded"] is False
    assert startup["active_page_id"] == "dashboard"
    assert startup["next_action"] == "Open the dashboard."
