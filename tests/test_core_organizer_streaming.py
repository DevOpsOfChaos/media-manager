from __future__ import annotations

from datetime import datetime
from pathlib import Path

from media_manager.core.organizer.models import OrganizePlannerOptions
from media_manager.core.organizer.planner import stream_organize_plan


def _resolution(path: Path, dt: datetime):
    from media_manager.core.date_resolver import DateResolution

    return DateResolution(
        path=path,
        resolved_datetime=dt,
        resolved_value=dt.strftime("%Y-%m-%d %H:%M:%S"),
        source_kind="metadata",
        source_label="EXIF:DateTimeOriginal",
        confidence="high",
        timezone_status="naive",
        reason="test fixture",
        candidates_checked=1,
    )


class TestStreamOrganizePlan:
    def test_yields_plan_entries(self, monkeypatch, tmp_path: Path) -> None:
        source = tmp_path / "source"
        target = tmp_path / "target"
        source.mkdir()
        target.mkdir()
        (source / "photo.jpg").write_bytes(b"jpg")

        monkeypatch.setattr(
            "media_manager.core.organizer.planner.resolve_capture_datetime",
            lambda file_path, exiftool_path=None, **kwargs: _resolution(file_path, datetime(2024, 8, 10, 11, 12, 13)),
        )

        options = OrganizePlannerOptions(
            source_dirs=(source,),
            target_root=target,
            pattern="{year}/{year_month_day}",
        )
        entries = list(stream_organize_plan(options))
        assert len(entries) == 1
        assert entries[0].status == "planned"
        assert entries[0].target_relative_dir.as_posix() == "2024/2024-08-10"

    def test_yields_multiple_files(self, monkeypatch, tmp_path: Path) -> None:
        source = tmp_path / "source"
        target = tmp_path / "target"
        source.mkdir()
        target.mkdir()
        (source / "a.jpg").write_bytes(b"jpg")
        (source / "b.jpg").write_bytes(b"jpg")

        monkeypatch.setattr(
            "media_manager.core.organizer.planner.resolve_capture_datetime",
            lambda file_path, exiftool_path=None, **kwargs: _resolution(file_path, datetime(2024, 8, 10, 11, 12, 13)),
        )

        options = OrganizePlannerOptions(
            source_dirs=(source,),
            target_root=target,
            pattern="{year}/{year_month_day}",
        )
        entries = list(stream_organize_plan(options))
        assert len(entries) == 2

    def test_empty_source_dir_yields_nothing(self, tmp_path: Path) -> None:
        source = tmp_path / "source"
        target = tmp_path / "target"
        source.mkdir()
        target.mkdir()

        options = OrganizePlannerOptions(
            source_dirs=(source,),
            target_root=target,
            pattern="{year}/{year_month_day}",
        )
        entries = list(stream_organize_plan(options))
        assert len(entries) == 0

    def test_missing_source_dir_is_handled(self, tmp_path: Path) -> None:
        source = tmp_path / "nonexistent"
        target = tmp_path / "target"
        target.mkdir()

        options = OrganizePlannerOptions(
            source_dirs=(source,),
            target_root=target,
            pattern="{year}/{year_month_day}",
        )
        entries = list(stream_organize_plan(options))
        for entry in entries:
            assert entry.status == "error"
