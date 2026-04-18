from __future__ import annotations

from datetime import datetime
from pathlib import Path

from media_manager.core.date_resolver import DateResolution
from media_manager.core.renamer import RenamePlannerOptions, build_rename_dry_run, execute_rename_dry_run


def _resolution(path: Path, dt: datetime | None = None) -> DateResolution:
    resolved = dt or datetime(2024, 8, 10, 11, 12, 13)
    return DateResolution(
        path=path,
        resolved_datetime=resolved,
        resolved_value=resolved.strftime("%Y-%m-%d %H:%M:%S"),
        source_kind="metadata",
        source_label="EXIF:DateTimeOriginal",
        confidence="high",
        timezone_status="naive",
        reason="test fixture",
        candidates_checked=1,
    )


def test_execute_rename_dry_run_captures_runtime_rename_errors(monkeypatch, tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    file_path = source / "IMG_0001.JPG"
    file_path.write_bytes(b"jpg")

    monkeypatch.setattr("media_manager.core.renamer.planner.resolve_capture_datetime", lambda path, exiftool_path=None: _resolution(path))

    original_rename = Path.rename

    def broken_rename(self: Path, target: Path):
        if self == file_path:
            raise OSError("simulated rename failure")
        return original_rename(self, target)

    monkeypatch.setattr(Path, "rename", broken_rename)

    dry_run = build_rename_dry_run(RenamePlannerOptions(source_dirs=(source,), template="{date:%Y-%m-%d}_{stem}"))
    execution = execute_rename_dry_run(dry_run, apply=True)

    assert execution.renamed_count == 0
    assert execution.error_count == 1
    assert execution.entries[0].status == "error"
    assert execution.entries[0].reason == "simulated rename failure"
    assert file_path.exists()
