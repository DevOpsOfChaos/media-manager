from __future__ import annotations

from pathlib import Path

from media_manager.cleanup_plan import build_exact_cleanup_dry_run, build_exact_group_id
from media_manager.duplicates import ExactDuplicateGroup
from media_manager.execution_plan import build_duplicate_execution_preview
from media_manager.execution_runner import run_duplicate_execution_preview


def _group(paths: list[Path], file_size: int = 1234, digest: str = "digest") -> ExactDuplicateGroup:
    return ExactDuplicateGroup(
        files=paths,
        file_size=file_size,
        sample_digest="sample",
        full_digest=digest,
        same_name=False,
        same_suffix=True,
    )


def test_preview_blocks_when_source_size_changed_since_scan(tmp_path: Path) -> None:
    keep = tmp_path / "keep.jpg"
    remove = tmp_path / "remove.jpg"
    keep.write_bytes(b"duplicate-bytes")
    remove.write_bytes(b"duplicate-bytes")

    group = _group([keep, remove], file_size=len(b"duplicate-bytes"), digest="size-change")
    decisions = {build_exact_group_id(group): str(keep)}
    dry_run = build_exact_cleanup_dry_run([group], decisions, "delete")
    preview = build_duplicate_execution_preview(dry_run)

    remove.write_bytes(b"changed-after-scan")
    result = run_duplicate_execution_preview(preview, apply=False)

    assert result.executed_rows == 0
    assert result.blocked_rows == 1
    assert result.error_rows == 0
    assert result.entries[0].reason == "source_size_changed_since_scan"
    assert remove.exists()


def test_preview_blocks_when_source_no_longer_matches_survivor(tmp_path: Path) -> None:
    keep = tmp_path / "keep.jpg"
    remove = tmp_path / "remove.jpg"
    keep.write_bytes(b"duplicate-bytes")
    remove.write_bytes(b"duplicate-bytes")

    group = _group([keep, remove], file_size=len(b"duplicate-bytes"), digest="content-change")
    decisions = {build_exact_group_id(group): str(keep)}
    dry_run = build_exact_cleanup_dry_run([group], decisions, "delete")
    preview = build_duplicate_execution_preview(dry_run)

    remove.write_bytes(b"DIFFERENT-CONTENT")
    remove.write_bytes(b"different-bytes")
    result = run_duplicate_execution_preview(preview, apply=False)

    assert result.executed_rows == 0
    assert result.blocked_rows == 1
    assert result.error_rows == 0
    assert result.entries[0].reason == "source_no_longer_matches_survivor"
    assert remove.exists()


def test_preview_blocks_when_survivor_is_missing(tmp_path: Path) -> None:
    keep = tmp_path / "keep.jpg"
    remove = tmp_path / "remove.jpg"
    keep.write_bytes(b"duplicate-bytes")
    remove.write_bytes(b"duplicate-bytes")

    group = _group([keep, remove], file_size=len(b"duplicate-bytes"), digest="missing-survivor")
    decisions = {build_exact_group_id(group): str(keep)}
    dry_run = build_exact_cleanup_dry_run([group], decisions, "delete")
    preview = build_duplicate_execution_preview(dry_run)

    keep.unlink()
    result = run_duplicate_execution_preview(preview, apply=False)

    assert result.executed_rows == 0
    assert result.blocked_rows == 1
    assert result.error_rows == 0
    assert result.entries[0].reason == "survivor_missing_on_disk"
    assert remove.exists()
