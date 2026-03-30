from __future__ import annotations

from pathlib import Path

from media_manager.cleanup_plan import build_exact_cleanup_dry_run, build_exact_group_id
from media_manager.duplicates import ExactDuplicateGroup
from media_manager.execution_plan import build_duplicate_execution_preview


def _group(paths: list[Path], file_size: int = 1234, digest: str = "digest") -> ExactDuplicateGroup:
    return ExactDuplicateGroup(
        files=paths,
        file_size=file_size,
        sample_digest="sample",
        full_digest=digest,
        same_name=False,
        same_suffix=True,
    )


def test_build_exact_cleanup_dry_run_for_delete_mode() -> None:
    keep = Path("/library/a/keep.jpg")
    remove = Path("/library/b/remove.jpg")
    group = _group([keep, remove], file_size=2048, digest="abc")
    decision = {build_exact_group_id(group): str(keep)}

    dry_run = build_exact_cleanup_dry_run([group], decision, "delete")

    assert dry_run.ready is True
    assert dry_run.planned_count == 1
    assert dry_run.blocked_count == 0
    assert dry_run.delete_count == 1

    row = dry_run.planned_actions[0]
    assert row.action_type == "delete"
    assert row.source_path == remove
    assert row.survivor_path == keep
    assert row.target_path is None
    assert row.status == "planned"


def test_build_exact_cleanup_dry_run_for_copy_mode_with_target_root() -> None:
    keep = Path("/library/a/keep.jpg")
    remove = Path("/library/b/remove.jpg")
    group = _group([keep, remove], file_size=2048, digest="copy")
    decision = {build_exact_group_id(group): str(keep)}

    dry_run = build_exact_cleanup_dry_run([group], decision, "copy", target_root="/target/library")

    assert dry_run.ready is True
    assert dry_run.exclude_from_copy_count == 1

    row = dry_run.planned_actions[0]
    assert row.action_type == "exclude_from_copy"
    assert row.target_path == Path("/target/library/remove.jpg")


def test_build_exact_cleanup_dry_run_marks_unresolved_groups_as_blocked() -> None:
    keep = Path("/library/a/keep.jpg")
    remove = Path("/library/b/remove.jpg")
    group = _group([keep, remove], file_size=2048, digest="blocked")

    dry_run = build_exact_cleanup_dry_run([group], {}, "move")

    assert dry_run.ready is False
    assert dry_run.planned_count == 0
    assert dry_run.blocked_count == 2
    assert all(row.action_type == "blocked_exact_group" for row in dry_run.blocked_actions)
    assert all(row.reason == "missing_keep_decision" for row in dry_run.blocked_actions)


def test_build_duplicate_execution_preview_maps_rows_by_mode() -> None:
    keep = Path("/library/a/keep.jpg")
    remove = Path("/library/b/remove.jpg")
    group = _group([keep, remove], file_size=2048, digest="exec")
    decision = {build_exact_group_id(group): str(keep)}

    delete_dry_run = build_exact_cleanup_dry_run([group], decision, "delete")
    delete_preview = build_duplicate_execution_preview(delete_dry_run)

    assert delete_preview.ready is True
    assert delete_preview.executable_count == 1
    assert delete_preview.deferred_count == 0
    assert delete_preview.blocked_count == 0
    assert delete_preview.delete_count == 1
    assert delete_preview.rows[0].row_type == "filesystem_delete"
    assert delete_preview.rows[0].status == "executable"

    move_dry_run = build_exact_cleanup_dry_run([group], decision, "move", target_root="/target/library")
    move_preview = build_duplicate_execution_preview(move_dry_run)

    assert move_preview.ready is True
    assert move_preview.executable_count == 0
    assert move_preview.deferred_count == 1
    assert move_preview.rows[0].row_type == "pipeline_exclusion"
    assert move_preview.rows[0].status == "deferred"


def test_build_duplicate_execution_preview_preserves_blocked_rows() -> None:
    first = Path("/library/a/one.jpg")
    second = Path("/library/b/two.jpg")
    group = _group([first, second], file_size=1024, digest="block_exec")

    dry_run = build_exact_cleanup_dry_run([group], {}, "delete")
    preview = build_duplicate_execution_preview(dry_run)

    assert preview.ready is False
    assert preview.blocked_count == 2
    assert preview.executable_count == 0
    assert all(row.row_type == "blocked" for row in preview.rows)
    assert all(row.status == "blocked" for row in preview.rows)
