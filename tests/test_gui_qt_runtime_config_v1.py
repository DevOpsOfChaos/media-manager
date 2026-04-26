from media_manager.core.gui_qt_runtime_config import build_qt_launch_args, build_qt_runtime_config


def test_runtime_config_normalizes_values_and_launch_args() -> None:
    config = build_qt_runtime_config(language="de-DE", theme="dark", density="spacious", start_page_id="people_review", people_bundle_dir="bundle")
    assert config["language"] == "de"
    assert config["theme"] == "modern-dark"
    assert config["density"] == "spacious"
    assert config["start_page_id"] == "people-review"
    assert config["summary"]["has_people_bundle"] is True
    args = build_qt_launch_args(config)
    assert args[:3] == ["media-manager-gui", "--active-page", "people-review"]
    assert "--people-bundle-dir" in args
