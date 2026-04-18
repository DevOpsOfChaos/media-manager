from __future__ import annotations

from datetime import date, datetime
from pathlib import Path

from media_manager.core.date_resolver import DateResolution
from media_manager.core.workflows import TripWorkflowOptions, build_trip_dry_run, execute_trip_plan, parse_trip_date


def _resolution(path: Path, dt: datetime) -> DateResolution:
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


def test_parse_trip_date_supports_iso_date() -> None:
    assert parse_trip_date("2025-08-10") == date(2025, 8, 10)


def test_build_trip_dry_run_selects_files_inside_range(monkeypatch, tmp_path: Path) -> None:
    source = tmp_path / "Phone"
    source.mkdir()
    inside = source / "inside.jpg"
    outside = source / "outside.jpg"
    inside.write_bytes(b"inside")
    outside.write_bytes(b"outside")

    def fake_resolve(path: Path, exiftool_path=None):
        if path.name == "inside.jpg":
            return _resolution(path, datetime(2025, 8, 10, 12, 0, 0))
        return _resolution(path, datetime(2025, 9, 1, 12, 0, 0))

    monkeypatch.setattr("media_manager.core.workflows.trip.resolve_capture_datetime", fake_resolve)

    dry_run = build_trip_dry_run(
        TripWorkflowOptions(
            source_dirs=(source,),
            target_root=tmp_path / "collections",
            label="Italy 2025",
            start_date=date(2025, 8, 1),
            end_date=date(2025, 8, 14),
        )
    )

    assert dry_run.media_file_count == 2
    assert dry_run.selected_count == 1
    assert dry_run.planned_count == 1
    assert dry_run.skipped_count == 1
    assert any(item.source_path == inside and item.status == "planned" for item in dry_run.entries)
    assert any(item.source_path == outside and item.status == "skipped" for item in dry_run.entries)


def test_build_trip_dry_run_skips_existing_matching_target(monkeypatch, tmp_path: Path) -> None:
    source = tmp_path / "Phone"
    source.mkdir()
    file_path = source / "photo.jpg"
    file_path.write_bytes(b"12345")

    monkeypatch.setattr(
        "media_manager.core.workflows.trip.resolve_capture_datetime",
        lambda path, exiftool_path=None: _resolution(path, datetime(2025, 8, 10, 12, 0, 0)),
    )

    target = tmp_path / "collections" / "Trips" / "2025" / "Italy_2025" / "Phone" / "photo.jpg"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(b"12345")

    dry_run = build_trip_dry_run(
        TripWorkflowOptions(
            source_dirs=(source,),
            target_root=tmp_path / "collections",
            label="Italy_2025",
            start_date=date(2025, 8, 1),
            end_date=date(2025, 8, 14),
        )
    )

    assert dry_run.planned_count == 0
    assert dry_run.skipped_count == 1
    assert dry_run.entries[0].reason == "target already exists with matching file size"


def test_execute_trip_plan_creates_hardlinks(monkeypatch, tmp_path: Path) -> None:
    source = tmp_path / "Phone"
    source.mkdir()
    file_path = source / "photo.jpg"
    file_path.write_bytes(b"photo-data")

    monkeypatch.setattr(
        "media_manager.core.workflows.trip.resolve_capture_datetime",
        lambda path, exiftool_path=None: _resolution(path, datetime(2025, 8, 10, 12, 0, 0)),
    )

    dry_run = build_trip_dry_run(
        TripWorkflowOptions(
            source_dirs=(source,),
            target_root=tmp_path / "collections",
            label="Italy_2025",
            start_date=date(2025, 8, 1),
            end_date=date(2025, 8, 14),
            mode="link",
        )
    )

    result = execute_trip_plan(dry_run, apply=True)

    assert result.executed_count == 1
    assert result.linked_count == 1
    target_path = result.entries[0].target_path
    assert target_path is not None and target_path.exists()
    assert file_path.exists()
    assert file_path.samefile(target_path)


def test_execute_trip_plan_can_copy(monkeypatch, tmp_path: Path) -> None:
    source = tmp_path / "Camera"
    source.mkdir()
    file_path = source / "photo.jpg"
    file_path.write_bytes(b"photo-data")

    monkeypatch.setattr(
        "media_manager.core.workflows.trip.resolve_capture_datetime",
        lambda path, exiftool_path=None: _resolution(path, datetime(2025, 8, 10, 12, 0, 0)),
    )

    dry_run = build_trip_dry_run(
        TripWorkflowOptions(
            source_dirs=(source,),
            target_root=tmp_path / "collections",
            label="Italy_2025",
            start_date=date(2025, 8, 1),
            end_date=date(2025, 8, 14),
            mode="copy",
        )
    )

    result = execute_trip_plan(dry_run, apply=True)

    assert result.executed_count == 1
    assert result.copied_count == 1
    target_path = result.entries[0].target_path
    assert target_path is not None and target_path.exists()
    assert file_path.exists()
    assert not file_path.samefile(target_path)
