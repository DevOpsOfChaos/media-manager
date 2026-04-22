from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from media_manager.cli_rename import main
from media_manager.core.date_resolver import DateResolution


def _resolution(path: Path) -> DateResolution:
    return DateResolution(
        path=path,
        resolved_datetime=datetime(2024, 8, 10, 11, 12, 13),
        resolved_value="2024-08-10 11:12:13",
        source_kind="metadata",
        source_label="EXIF:DateTimeOriginal",
        confidence="high",
        timezone_status="naive",
        reason="test fixture",
        candidates_checked=1,
    )


def test_cli_rename_json_output_contains_summary(monkeypatch, tmp_path: Path, capsys) -> None:
    source = tmp_path / "source"
    source.mkdir()
    (source / "IMG_0001.JPG").write_bytes(b"jpg")

    monkeypatch.setattr(
        "media_manager.core.renamer.planner.resolve_capture_datetime",
        lambda path, exiftool_path=None: _resolution(path),
    )

    exit_code = main(["--source", str(source), "--json"])
    captured = capsys.readouterr()

    assert exit_code == 0
    payload = json.loads(captured.out)
    assert payload["media_file_count"] == 1
    assert payload["planned_count"] == 1


def test_cli_rename_include_associated_files_groups_sidecar_in_json(monkeypatch, tmp_path: Path, capsys) -> None:
    source = tmp_path / "source"
    source.mkdir()
    (source / "IMG_0001.JPG").write_bytes(b"jpg")
    (source / "IMG_0001.xmp").write_text("xmp", encoding="utf-8")

    monkeypatch.setattr(
        "media_manager.core.renamer.planner.resolve_capture_datetime",
        lambda path, exiftool_path=None: _resolution(path),
    )

    exit_code = main(["--source", str(source), "--include-associated-files", "--json"])
    captured = capsys.readouterr()

    assert exit_code == 0
    payload = json.loads(captured.out)
    assert payload["media_group_count"] == 1
    assert payload["associated_file_count"] == 1
    assert payload["group_kind_summary"] == {"sidecar": 1}
    assert payload["entries"][0]["group_kind"] == "sidecar"
    assert payload["entries"][0]["associated_file_count"] == 1
    assert payload["entries"][0]["associated_files"] == [str(source / "IMG_0001.xmp")]


def test_cli_rename_apply_reports_rename_execution(monkeypatch, tmp_path: Path, capsys) -> None:
    source = tmp_path / "source"
    source.mkdir()
    (source / "IMG_0001.JPG").write_bytes(b"jpg")

    monkeypatch.setattr(
        "media_manager.core.renamer.planner.resolve_capture_datetime",
        lambda path, exiftool_path=None: _resolution(path),
    )

    exit_code = main(["--source", str(source), "--json", "--apply"])
    captured = capsys.readouterr()

    assert exit_code == 0
    payload = json.loads(captured.out)
    assert payload["execution"]["apply_requested"] is True
    assert payload["execution"]["renamed_count"] == 1
    assert payload["execution"]["entries"][0]["action"] == "renamed"


def test_cli_rename_apply_with_associated_files_renames_sidecar_and_journals_each_member(monkeypatch, tmp_path: Path, capsys) -> None:
    source = tmp_path / "source"
    source.mkdir()
    photo = source / "IMG_0001.JPG"
    sidecar = source / "IMG_0001.xmp"
    photo.write_bytes(b"jpg")
    sidecar.write_text("xmp", encoding="utf-8")
    journal_path = tmp_path / "journals" / "rename-execution.json"

    monkeypatch.setattr(
        "media_manager.core.renamer.planner.resolve_capture_datetime",
        lambda path, exiftool_path=None: _resolution(path),
    )

    exit_code = main(
        [
            "--source",
            str(source),
            "--include-associated-files",
            "--apply",
            "--json",
            "--journal",
            str(journal_path),
        ]
    )
    captured = capsys.readouterr()

    assert exit_code == 0
    payload = json.loads(captured.out)
    assert payload["execution"]["renamed_count"] == 1
    entry = payload["execution"]["entries"][0]
    assert entry["group_kind"] == "sidecar"
    assert entry["associated_file_count"] == 1
    assert len(entry["member_results"]) == 2
    assert {item["action"] for item in entry["member_results"]} == {"renamed"}

    journal = json.loads(journal_path.read_text(encoding="utf-8"))
    assert journal["command_name"] == "rename"
    assert journal["apply_requested"] is True
    assert journal["entry_count"] == 2
    assert journal["reversible_entry_count"] == 2
    assert {item["outcome"] for item in journal["entries"]} == {"renamed"}
    assert {Path(item["source_path"]).name for item in journal["entries"]} == {"IMG_0001.JPG", "IMG_0001.xmp"}

    renamed_photo = next(item for item in entry["member_results"] if item["is_main_file"] is True)
    renamed_sidecar = next(item for item in entry["member_results"] if item["is_main_file"] is False)
    assert Path(renamed_photo["target_path"]).exists()
    assert Path(renamed_sidecar["target_path"]).exists()


def test_cli_rename_writes_run_log(monkeypatch, tmp_path: Path, capsys) -> None:
    source = tmp_path / "source"
    source.mkdir()
    (source / "IMG_0001.JPG").write_bytes(b"jpg")
    log_path = tmp_path / "logs" / "rename-run.json"

    monkeypatch.setattr(
        "media_manager.core.renamer.planner.resolve_capture_datetime",
        lambda path, exiftool_path=None: _resolution(path),
    )

    exit_code = main(["--source", str(source), "--json", "--run-log", str(log_path)])
    captured = capsys.readouterr()

    assert exit_code == 0
    payload = json.loads(captured.out)
    run_log = json.loads(log_path.read_text(encoding="utf-8"))
    assert run_log["command_name"] == "rename"
    assert run_log["apply_requested"] is False
    assert run_log["exit_code"] == 0
    assert run_log["payload"]["planned_count"] == payload["planned_count"]


def test_cli_rename_apply_writes_execution_journal(monkeypatch, tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    (source / "IMG_0001.JPG").write_bytes(b"jpg")
    journal_path = tmp_path / "journals" / "rename-execution.json"

    monkeypatch.setattr(
        "media_manager.core.renamer.planner.resolve_capture_datetime",
        lambda path, exiftool_path=None: _resolution(path),
    )

    exit_code = main(["--source", str(source), "--apply", "--journal", str(journal_path)])

    assert exit_code == 0
    payload = json.loads(journal_path.read_text(encoding="utf-8"))
    assert payload["command_name"] == "rename"
    assert payload["apply_requested"] is True
    assert payload["entries"][0]["outcome"] == "renamed"
    assert payload["entries"][0]["undo_action"] == "rename_back"


def test_cli_rename_history_dir_writes_auto_named_run_log(monkeypatch, tmp_path: Path, capsys) -> None:
    source = tmp_path / "source"
    source.mkdir()
    (source / "IMG_0001.JPG").write_bytes(b"jpg")
    history_dir = tmp_path / "history"

    monkeypatch.setattr(
        "media_manager.core.renamer.planner.resolve_capture_datetime",
        lambda path, exiftool_path=None: _resolution(path),
    )

    exit_code = main(["--source", str(source), "--json", "--history-dir", str(history_dir)])
    captured = capsys.readouterr()

    assert exit_code == 0
    payload = json.loads(captured.out)

    files = sorted(history_dir.glob("*.json"))
    assert len(files) == 1
    run_log_path = files[0]

    assert "-rename-preview-run-log.json" in run_log_path.name

    run_log = json.loads(run_log_path.read_text(encoding="utf-8"))
    assert run_log["command_name"] == "rename"
    assert run_log["payload"]["planned_count"] == payload["planned_count"]
