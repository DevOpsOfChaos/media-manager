from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

from media_manager.cli_organize import main as organize_main
from media_manager.cli_rename import main as rename_main


def test_cli_organize_json_includes_summary_blocks(monkeypatch, capsys, tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    target = tmp_path / "target"
    target.mkdir()

    fake_entry = SimpleNamespace(
        source_root=source,
        source_path=source / "a.jpg",
        scanned_file=SimpleNamespace(relative_path=Path("a.jpg")),
        status="planned",
        reason="ready",
        operation_mode="copy",
        target_relative_dir=Path("2024/2024-08-10"),
        target_path=target / "2024" / "2024-08-10" / "a.jpg",
        resolution=SimpleNamespace(resolved_value="2024-08-10 11:12:13", source_kind="metadata", source_label="EXIF:DateTimeOriginal", confidence="high"),
    )
    fake_plan = SimpleNamespace(
        options=SimpleNamespace(source_dirs=(source,), target_root=target, pattern="{year}/{year_month_day}", operation_mode="copy"),
        scan_summary=SimpleNamespace(missing_sources=[]),
        media_file_count=1,
        planned_count=1,
        skipped_count=0,
        conflict_count=0,
        error_count=0,
        missing_source_count=0,
        entries=[fake_entry],
    )
    monkeypatch.setattr("media_manager.cli_organize.build_organize_dry_run", lambda options, **kwargs: fake_plan)
    monkeypatch.setattr("media_manager.cli_organize.execute_organize_plan", lambda plan, **kwargs: None)

    code = organize_main(["--source", str(source), "--target", str(target), "--json"])
    payload = json.loads(capsys.readouterr().out)

    assert code == 0
    assert payload["status_summary"] == {"planned": 1}
    assert payload["resolution_source_summary"] == {"metadata": 1}


def test_cli_rename_json_includes_summary_blocks(monkeypatch, capsys, tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()

    fake_entry = SimpleNamespace(
        source_path=source / "a.jpg",
        target_path=source / "2024-08-10_a.jpg",
        rendered_name="2024-08-10_a.jpg",
        status="planned",
        reason="ready",
        resolution=SimpleNamespace(resolved_value="2024-08-10 11:12:13", source_kind="metadata", source_label="EXIF:DateTimeOriginal", confidence="high"),
    )
    fake_dry_run = SimpleNamespace(
        options=SimpleNamespace(template="{date:%Y-%m-%d}_{stem}", source_dirs=(source,)),
        scan_summary=SimpleNamespace(missing_sources=[]),
        media_file_count=1,
        planned_count=1,
        skipped_count=0,
        conflict_count=0,
        error_count=0,
        missing_source_count=0,
        entries=[fake_entry],
    )
    fake_execution = SimpleNamespace(
        apply_requested=False,
        processed_count=1,
        preview_count=1,
        renamed_count=0,
        skipped_count=0,
        conflict_count=0,
        error_count=0,
        entries=[SimpleNamespace(source_path=fake_entry.source_path, target_path=fake_entry.target_path, status="planned", reason="ready", action="preview-rename")],
    )
    monkeypatch.setattr("media_manager.cli_rename.build_rename_dry_run", lambda options: fake_dry_run)
    monkeypatch.setattr("media_manager.cli_rename.execute_rename_dry_run", lambda dry_run, apply=False: fake_execution)

    code = rename_main(["--source", str(source), "--json"])
    payload = json.loads(capsys.readouterr().out)

    assert code == 0
    assert payload["status_summary"] == {"planned": 1}
    assert payload["execution"]["action_summary"] == {"preview-rename": 1}
