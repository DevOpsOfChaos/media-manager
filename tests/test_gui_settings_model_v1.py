from __future__ import annotations

from pathlib import Path

from media_manager.core.gui_settings_model import load_gui_settings, update_gui_settings, write_gui_settings


def test_settings_round_trip(tmp_path: Path) -> None:
    path = tmp_path / "gui-settings.json"
    settings = update_gui_settings({}, language="de", theme="modern-light", recent_paths={"people_bundle_dir": "bundle"})
    write_gui_settings(path, settings)

    loaded = load_gui_settings(path)
    assert loaded["language"] == "de"
    assert loaded["theme"] == "modern-light"
    assert loaded["recent_paths"]["people_bundle_dir"] == "bundle"
