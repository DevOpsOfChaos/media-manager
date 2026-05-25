from __future__ import annotations

from datetime import datetime
from pathlib import Path

from media_manager.core.date_resolver import DateResolution
from media_manager.core.organizer import (
    DEFAULT_ORGANIZE_PATTERN,
    OrganizePlannerOptions,
    build_organize_dry_run,
    execute_organize_plan,
    render_organize_directory,
)


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


def test_render_organize_directory_uses_supported_tokens() -> None:
    resolution = _resolution(Path("photo.jpg"), datetime(2024, 8, 10, 11, 12, 13))
    rendered = render_organize_directory("{year}/{year_month_day}/{source_name}", resolution, source_root=Path("/imports/phone"))
    assert rendered.as_posix() == "2024/2024-08-10/phone"


def test_build_organize_dry_run_plans_target_paths(monkeypatch, tmp_path: Path) -> None:
    source = tmp_path / "source"
    target = tmp_path / "target"
    source.mkdir(); target.mkdir()
    photo = source / "photo.jpg"
    photo.write_bytes(b"jpg")
    monkeypatch.setattr("media_manager.core.organizer.planner.resolve_capture_datetime", lambda file_path, exiftool_path=None, **kwargs: _resolution(file_path, datetime(2024, 8, 10, 11, 12, 13)))
    plan = build_organize_dry_run(OrganizePlannerOptions(source_dirs=(source,), target_root=target, pattern=DEFAULT_ORGANIZE_PATTERN))
    assert plan.media_file_count == 1
    assert plan.planned_count == 1
    assert plan.conflict_count == 0
    entry = plan.entries[0]
    assert entry.status == "planned"
    assert entry.target_relative_dir.as_posix() == "2024/2024-08-10"
    assert entry.target_path == target / "2024" / "2024-08-10" / "photo.jpg"


def test_build_organize_dry_run_marks_existing_target_as_conflict_when_bytes_differ(monkeypatch, tmp_path: Path) -> None:
    source = tmp_path / "source"; target = tmp_path / "target"
    source.mkdir(); target.mkdir()
    photo = source / "photo.jpg"
    photo.write_bytes(b"same-size-a")
    existing_target = target / "2024" / "2024-08-10"
    existing_target.mkdir(parents=True)
    (existing_target / "photo.jpg").write_bytes(b"same-size-b")
    monkeypatch.setattr("media_manager.core.organizer.planner.resolve_capture_datetime", lambda file_path, exiftool_path=None, **kwargs: _resolution(file_path, datetime(2024, 8, 10, 11, 12, 13)))
    plan = build_organize_dry_run(OrganizePlannerOptions(source_dirs=(source,), target_root=target, pattern=DEFAULT_ORGANIZE_PATTERN))
    assert plan.planned_count == 0
    assert plan.conflict_count == 1
    assert plan.entries[0].status == "conflict"
    assert plan.entries[0].reason == "target path already exists"


def test_build_organize_dry_run_skips_existing_identical_target(monkeypatch, tmp_path: Path) -> None:
    source = tmp_path / "source"; target = tmp_path / "target"
    source.mkdir(); target.mkdir()
    photo = source / "photo.jpg"
    photo.write_bytes(b"same-bytes")
    existing_target = target / "2024" / "2024-08-10"
    existing_target.mkdir(parents=True)
    (existing_target / "photo.jpg").write_bytes(b"same-bytes")
    monkeypatch.setattr("media_manager.core.organizer.planner.resolve_capture_datetime", lambda file_path, exiftool_path=None, **kwargs: _resolution(file_path, datetime(2024, 8, 10, 11, 12, 13)))
    plan = build_organize_dry_run(OrganizePlannerOptions(source_dirs=(source,), target_root=target, pattern=DEFAULT_ORGANIZE_PATTERN))
    assert plan.skipped_count == 1
    assert plan.entries[0].status == "skipped"
    assert plan.entries[0].reason == "target already exists with identical file content"


def test_build_organize_dry_run_marks_same_target_path_collisions(monkeypatch, tmp_path: Path) -> None:
    source_a = tmp_path / "source_a"; source_b = tmp_path / "source_b"; target = tmp_path / "target"
    source_a.mkdir(); source_b.mkdir(); target.mkdir()
    (source_a / "photo.jpg").write_bytes(b"a")
    (source_b / "photo.jpg").write_bytes(b"b")
    monkeypatch.setattr("media_manager.core.organizer.planner.resolve_capture_datetime", lambda file_path, exiftool_path=None, **kwargs: _resolution(file_path, datetime(2024, 8, 10, 11, 12, 13)))
    plan = build_organize_dry_run(OrganizePlannerOptions(source_dirs=(source_a, source_b), target_root=target, pattern=DEFAULT_ORGANIZE_PATTERN))
    assert plan.planned_count == 0
    assert plan.conflict_count == 2
    assert {item.reason for item in plan.entries} == {"multiple source files would resolve to the same target path"}


def test_rename_conflict_policy_avoids_collision(monkeypatch, tmp_path: Path) -> None:
    source = tmp_path / "source"; target = tmp_path / "target"
    source.mkdir(); target.mkdir()
    jpg1 = source / "photo.jpg"
    jpg2 = source / "photo2.jpg"
    jpg1.write_bytes(b"jpg1")
    jpg2.write_bytes(b"jpg2")
    collision_target = target / "2024" / "2024-08-10"
    collision_target.mkdir(parents=True)
    (collision_target / "photo2.jpg").write_bytes(b"existing")
    monkeypatch.setattr("media_manager.core.organizer.planner.resolve_capture_datetime", lambda file_path, exiftool_path=None, **kwargs: _resolution(file_path, datetime(2024, 8, 10, 11, 12, 13)))
    plan = build_organize_dry_run(OrganizePlannerOptions(
        source_dirs=(source,), target_root=target, pattern=DEFAULT_ORGANIZE_PATTERN,
        conflict_policy="rename", operation_mode="copy"
    ))
    assert plan.conflict_count == 0
    assert plan.planned_count == 2
    paths = [str(e.target_path) for e in plan.entries]
    assert any("_1" in p for p in paths)


def test_build_organize_dry_run_skips_source_already_in_target_location(monkeypatch, tmp_path: Path) -> None:
    target = tmp_path / "target"
    planned_dir = target / "2024" / "2024-08-10"
    planned_dir.mkdir(parents=True)
    photo = planned_dir / "photo.jpg"
    photo.write_bytes(b"jpg")
    monkeypatch.setattr("media_manager.core.organizer.planner.resolve_capture_datetime", lambda file_path, exiftool_path=None, **kwargs: _resolution(file_path, datetime(2024, 8, 10, 11, 12, 13)))
    plan = build_organize_dry_run(OrganizePlannerOptions(source_dirs=(planned_dir,), target_root=target, pattern=DEFAULT_ORGANIZE_PATTERN, recursive=False))
    assert plan.skipped_count == 1
    assert plan.entries[0].status == "skipped"
    assert plan.entries[0].reason == "source already matches the planned target path"


def test_execute_organize_plan_copies_planned_entries(monkeypatch, tmp_path: Path) -> None:
    source = tmp_path / "source"; target = tmp_path / "target"
    source.mkdir(); target.mkdir()
    photo = source / "photo.jpg"
    photo.write_bytes(b"jpg")
    monkeypatch.setattr("media_manager.core.organizer.planner.resolve_capture_datetime", lambda file_path, exiftool_path=None, **kwargs: _resolution(file_path, datetime(2024, 8, 10, 11, 12, 13)))
    plan = build_organize_dry_run(OrganizePlannerOptions(source_dirs=(source,), target_root=target, pattern=DEFAULT_ORGANIZE_PATTERN, operation_mode="copy"))
    result = execute_organize_plan(plan)
    assert result.executed_count == 1
    assert result.copied_count == 1
    assert result.error_count == 0
    assert photo.exists()
    assert (target / "2024" / "2024-08-10" / "photo.jpg").exists()


def test_execute_organize_plan_moves_planned_entries(monkeypatch, tmp_path: Path) -> None:
    source = tmp_path / "source"; target = tmp_path / "target"
    source.mkdir(); target.mkdir()
    photo = source / "photo.jpg"
    photo.write_bytes(b"jpg")
    monkeypatch.setattr("media_manager.core.organizer.planner.resolve_capture_datetime", lambda file_path, exiftool_path=None, **kwargs: _resolution(file_path, datetime(2024, 8, 10, 11, 12, 13)))
    plan = build_organize_dry_run(OrganizePlannerOptions(source_dirs=(source,), target_root=target, pattern=DEFAULT_ORGANIZE_PATTERN, operation_mode="move"))
    result = execute_organize_plan(plan)
    assert result.executed_count == 1
    assert result.moved_count == 1
    assert result.error_count == 0
    assert not photo.exists()
    assert (target / "2024" / "2024-08-10" / "photo.jpg").exists()


def test_execute_organize_plan_skips_identical_target_that_appears_after_planning(monkeypatch, tmp_path: Path) -> None:
    source = tmp_path / "source"; target = tmp_path / "target"
    source.mkdir(); target.mkdir()
    photo = source / "photo.jpg"
    photo.write_bytes(b"same-bytes")
    monkeypatch.setattr("media_manager.core.organizer.planner.resolve_capture_datetime", lambda file_path, exiftool_path=None, **kwargs: _resolution(file_path, datetime(2024, 8, 10, 11, 12, 13)))
    plan = build_organize_dry_run(OrganizePlannerOptions(source_dirs=(source,), target_root=target, pattern=DEFAULT_ORGANIZE_PATTERN, operation_mode="copy"))
    plan.entries[0].target_path.parent.mkdir(parents=True)
    plan.entries[0].target_path.write_bytes(b"same-bytes")
    result = execute_organize_plan(plan)
    assert result.executed_count == 0
    assert result.skipped_count == 1
    assert result.entries[0].reason == "target already exists with identical file content at apply time"


# --- media groups integration ---

def test_include_associated_files_sidecar_group_one_entry(monkeypatch, tmp_path: Path) -> None:
    source = tmp_path / "source"; target = tmp_path / "target"
    source.mkdir(); target.mkdir()
    jpg = source / "photo.jpg"
    xmp = source / "photo.xmp"
    jpg.write_bytes(b"jpg"); xmp.write_bytes(b"xmp")
    monkeypatch.setattr("media_manager.core.organizer.planner.resolve_capture_datetime", lambda file_path, exiftool_path=None, **kwargs: _resolution(file_path, datetime(2024, 8, 10, 11, 12, 13)))
    plan = build_organize_dry_run(OrganizePlannerOptions(source_dirs=(source,), target_root=target, pattern=DEFAULT_ORGANIZE_PATTERN, include_associated_files=True))
    assert plan.planned_count == 1
    entry = plan.entries[0]
    assert entry.source_path == jpg
    assert entry.media_group is not None
    assert entry.group_kind == "sidecar"
    assert entry.group_id is not None
    assert entry.group_id.startswith("media-group-")


def test_include_associated_files_group_target_paths_cover_all_members(monkeypatch, tmp_path: Path) -> None:
    source = tmp_path / "source"; target = tmp_path / "target"
    source.mkdir(); target.mkdir()
    jpg = source / "photo.jpg"
    xmp = source / "photo.xmp"
    jpg.write_bytes(b"jpg"); xmp.write_bytes(b"xmp")
    monkeypatch.setattr("media_manager.core.organizer.planner.resolve_capture_datetime", lambda file_path, exiftool_path=None, **kwargs: _resolution(file_path, datetime(2024, 8, 10, 11, 12, 13)))
    plan = build_organize_dry_run(OrganizePlannerOptions(source_dirs=(source,), target_root=target, pattern=DEFAULT_ORGANIZE_PATTERN, include_associated_files=True))
    entry = plan.entries[0]
    assert len(entry.group_target_paths) >= 2
    assert jpg in entry.group_target_paths
    assert xmp in entry.group_target_paths
    assert entry.group_target_paths[jpg] is not None
    assert entry.group_target_paths[xmp] is not None


def test_include_associated_files_false_no_group_data(monkeypatch, tmp_path: Path) -> None:
    source = tmp_path / "source"; target = tmp_path / "target"
    source.mkdir(); target.mkdir()
    jpg = source / "photo.jpg"
    xmp = source / "photo.xmp"
    jpg.write_bytes(b"jpg"); xmp.write_bytes(b"xmp")
    monkeypatch.setattr("media_manager.core.organizer.planner.resolve_capture_datetime", lambda file_path, exiftool_path=None, **kwargs: _resolution(file_path, datetime(2024, 8, 10, 11, 12, 13)))
    plan = build_organize_dry_run(OrganizePlannerOptions(source_dirs=(source,), target_root=target, pattern=DEFAULT_ORGANIZE_PATTERN, include_associated_files=False))
    for entry in plan.entries:
        assert entry.media_group is None
        assert entry.group_kind is None
        assert entry.group_id is None
        assert len(entry.group_target_paths) == 1


def test_include_associated_files_raw_jpeg_pair_group_kind(monkeypatch, tmp_path: Path) -> None:
    source = tmp_path / "source"; target = tmp_path / "target"
    source.mkdir(); target.mkdir()
    raw = source / "photo.cr3"
    jpg = source / "photo.jpg"
    raw.write_bytes(b"raw"); jpg.write_bytes(b"jpg")
    monkeypatch.setattr("media_manager.core.organizer.planner.resolve_capture_datetime", lambda file_path, exiftool_path=None, **kwargs: _resolution(file_path, datetime(2024, 8, 10, 11, 12, 13)))
    plan = build_organize_dry_run(OrganizePlannerOptions(source_dirs=(source,), target_root=target, pattern=DEFAULT_ORGANIZE_PATTERN, include_associated_files=True))
    assert plan.planned_count == 1
    assert plan.entries[0].group_kind == "raw_jpeg_pair"


def test_organize_dry_run_group_summary_properties(monkeypatch, tmp_path: Path) -> None:
    source = tmp_path / "source"; target = tmp_path / "target"
    source.mkdir(); target.mkdir()
    jpg = source / "photo.jpg"
    xmp = source / "photo.xmp"
    jpg.write_bytes(b"jpg"); xmp.write_bytes(b"xmp")
    monkeypatch.setattr("media_manager.core.organizer.planner.resolve_capture_datetime", lambda file_path, exiftool_path=None, **kwargs: _resolution(file_path, datetime(2024, 8, 10, 11, 12, 13)))
    plan = build_organize_dry_run(OrganizePlannerOptions(source_dirs=(source,), target_root=target, pattern=DEFAULT_ORGANIZE_PATTERN, include_associated_files=True))
    assert plan.media_group_count >= 1
    assert plan.associated_file_count >= 1
    assert plan.group_kind_summary == {"sidecar": 1}


def test_execute_organize_group_copy_moves_all_members(monkeypatch, tmp_path: Path) -> None:
    """When include_associated_files=True and operation_mode=copy, all group members are copied."""
    source = tmp_path / "source"; target = tmp_path / "target"
    source.mkdir(); target.mkdir()
    jpg = source / "photo.jpg"
    xmp = source / "photo.xmp"
    jpg.write_bytes(b"jpg"); xmp.write_bytes(b"xmp")
    monkeypatch.setattr("media_manager.core.organizer.planner.resolve_capture_datetime", lambda file_path, exiftool_path=None, **kwargs: _resolution(file_path, datetime(2024, 8, 10, 11, 12, 13)))
    plan = build_organize_dry_run(OrganizePlannerOptions(source_dirs=(source,), target_root=target, pattern=DEFAULT_ORGANIZE_PATTERN, include_associated_files=True, operation_mode="copy"))
    result = execute_organize_plan(plan)
    assert result.executed_count == 1
    assert result.copied_count == 1
    for entry in result.entries:
        assert len(entry.member_results) >= 2
        outcomes = {mr.outcome for mr in entry.member_results}
        assert outcomes == {"copied"}
    assert jpg.exists()
    assert xmp.exists()
    assert (target / "2024" / "2024-08-10" / "photo.jpg").exists()
    assert (target / "2024" / "2024-08-10" / "photo.xmp").exists()


def test_execute_organize_group_move_moves_all_members(monkeypatch, tmp_path: Path) -> None:
    """When include_associated_files=True and operation_mode=move, all group members are moved."""
    source = tmp_path / "source"; target = tmp_path / "target"
    source.mkdir(); target.mkdir()
    jpg = source / "photo.jpg"
    xmp = source / "photo.xmp"
    jpg.write_bytes(b"jpg"); xmp.write_bytes(b"xmp")
    monkeypatch.setattr("media_manager.core.organizer.planner.resolve_capture_datetime", lambda file_path, exiftool_path=None, **kwargs: _resolution(file_path, datetime(2024, 8, 10, 11, 12, 13)))
    plan = build_organize_dry_run(OrganizePlannerOptions(source_dirs=(source,), target_root=target, pattern=DEFAULT_ORGANIZE_PATTERN, include_associated_files=True, operation_mode="move"))
    result = execute_organize_plan(plan)
    assert result.executed_count == 1
    assert result.moved_count == 1
    for entry in result.entries:
        assert len(entry.member_results) >= 2
        outcomes = {mr.outcome for mr in entry.member_results}
        assert outcomes == {"moved"}
    assert not jpg.exists()
    assert not xmp.exists()
    assert (target / "2024" / "2024-08-10" / "photo.jpg").exists()
    assert (target / "2024" / "2024-08-10" / "photo.xmp").exists()


def test_organize_group_journal_and_undo_roundtrip(monkeypatch, tmp_path: Path) -> None:
    """Full pipeline: organize a group (copy), verify journal entries per member, undo restores state."""
    from media_manager.core.state.execution_journal import load_execution_journal, write_execution_journal
    from media_manager.core.state.undo import execute_undo_journal

    source = tmp_path / "source"; target = tmp_path / "target"
    source.mkdir(); target.mkdir()
    jpg = source / "photo.jpg"
    xmp = source / "photo.xmp"
    jpg.write_bytes(b"jpg-content")
    xmp.write_bytes(b"xmp-content")

    monkeypatch.setattr("media_manager.core.organizer.planner.resolve_capture_datetime", lambda file_path, exiftool_path=None, **kwargs: _resolution(file_path, datetime(2024, 8, 10, 11, 12, 13)))

    # 1. Plan + execute organize with groups (copy mode)
    plan = build_organize_dry_run(OrganizePlannerOptions(source_dirs=(source,), target_root=target, pattern=DEFAULT_ORGANIZE_PATTERN, include_associated_files=True, operation_mode="copy"))
    result = execute_organize_plan(plan)
    assert result.copied_count == 1

    # 2. Build journal entries (simulating what cli_organize does)
    journal_entries = []
    for item in result.entries:
        for member in getattr(item, "member_results", ()):
            reversible = member.outcome == "copied"
            undo_action = "delete_target" if reversible else None
            entry = {
                "outcome": member.outcome,
                "reversible": reversible,
                "undo_action": undo_action,
                "undo_from_path": str(member.target_path) if reversible and member.target_path is not None else None,
                "undo_to_path": None,
            }
            journal_entries.append(entry)

    assert len(journal_entries) == 2
    assert all(e["reversible"] for e in journal_entries)

    # 3. Write journal
    journal_path = tmp_path / "journal.json"
    write_execution_journal(journal_path, command_name="organize", apply_requested=True, exit_code=0, entries=journal_entries)

    # 4. Undo
    undo_result = execute_undo_journal(journal_path, apply=True)
    assert undo_result.undone_count == 2
    assert undo_result.error_count == 0

    # 5. Verify original files still exist, targets are gone
    assert jpg.exists()
    assert xmp.exists()
    assert not (target / "2024" / "2024-08-10" / "photo.jpg").exists()
    assert not (target / "2024" / "2024-08-10" / "photo.xmp").exists()
