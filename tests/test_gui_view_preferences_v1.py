from pathlib import Path

from media_manager.core.gui_view_preferences import load_view_preferences, normalize_view_preferences, save_view_preferences


def test_view_preferences_normalize_invalid_values() -> None:
    prefs = normalize_view_preferences({"language": "fr", "theme": "neon", "density": "tiny"})

    assert prefs["language"] == "en"
    assert prefs["theme"] == "modern-dark"
    assert prefs["density"] == "comfortable"


def test_view_preferences_round_trip(tmp_path: Path) -> None:
    path = tmp_path / "prefs.json"
    save_view_preferences(path, {"language": "de", "theme": "modern-light", "density": "compact"})

    loaded = load_view_preferences(path)

    assert loaded["language"] == "de"
    assert loaded["theme"] == "modern-light"
    assert loaded["density"] == "compact"
