from pathlib import Path

from media_manager.core.gui_folder_picker_model import build_folder_picker_model, build_standard_folder_pickers


def test_folder_picker_validates_missing_required_path() -> None:
    picker = build_folder_picker_model("source", required=True)

    assert picker["valid"] is True
    assert picker["problem_count"] == 1
    assert picker["problems"][0]["code"] == "path_required"


def test_folder_picker_detects_existing_directory(tmp_path: Path) -> None:
    picker = build_folder_picker_model("run_dir", path=tmp_path, must_exist=True)

    assert picker["value"]["exists"] is True
    assert picker["value"]["is_dir"] is True
    assert picker["valid"] is True


def test_standard_folder_pickers_returns_four_pickers() -> None:
    payload = build_standard_folder_pickers()

    assert payload["kind"] == "folder_picker_set"
    assert len(payload["pickers"]) == 4
