from __future__ import annotations

import os
import time
from pathlib import Path

from media_manager.duplicate_workflow import (
    build_duplicate_decisions,
    build_duplicate_workflow_bundle,
    build_duplicate_workflow_from_scan,
    choose_keep_path,
    execute_duplicate_workflow_bundle,
)
from media_manager.duplicates import DuplicateScanConfig, ExactDuplicateGroup, scan_exact_duplicates


def _group(paths: list[Path], file_size: int = 1234, digest: str = "digest") -> ExactDuplicateGroup:
    return ExactDuplicateGroup(
        files=paths,
        file_size=file_size,
        sample_digest="sample",
        full_digest=digest,
        same_name=False,
        same_suffix=True,
    )


def test_choose_keep_path_supports_first_newest_and_oldest(tmp_path: Path) -> None:
    first = tmp_path / "first.jpg"
    second = tmp_path / "second.jpg"
    third = tmp_path / "third.jpg"

    first.write_bytes(b"1")
    second.write_bytes(b"2")
    third.write_bytes(b"3")

    now = time.time()
    first_ts = now - 30
    second_ts = now - 20
    third_ts = now - 10
    os.utime(first, (first_ts, first_ts))
    os.utime(second, (second_ts, second_ts))
    os.utime(third, (third_ts, third_ts))

    group = _group([first, second, third], digest="policy")

    assert choose_keep_path(group, "first") == first
    assert choose_keep_path(group, "newest") == third
    assert choose_keep_path(group, "oldest") == first


def test_build_duplicate_decisions_creates_group_id_mapping(tmp_path: Path) -> None:
    first = tmp_path / "first.jpg"
    second = tmp_path / "second.jpg"
    first.write_bytes(b"a")
    second.write_bytes(b"b")

    group = _group([first, second], digest="mapping")
    decisions = build_duplicate_decisions([group], "first")

    assert list(decisions.values()) == [str(first)]
    assert len(decisions) == 1


def test_build_duplicate_workflow_bundle_composes_plan_dry_run_and_execution(tmp_path: Path) -> None:
    keep = tmp_path / "keep.jpg"
    remove = tmp_path / "remove.jpg"
    keep.write_bytes(b"same")
    remove.write_bytes(b"same")

    group = _group([keep, remove], file_size=4, digest="bundle")
    decisions = build_duplicate_decisions([group], "first")
    bundle = build_duplicate_workflow_bundle([group], decisions, "delete")

    assert bundle.cleanup_plan.ready_for_dry_run is True
    assert bundle.cleanup_plan.resolved_groups == 1
    assert bundle.dry_run.ready is True
    assert bundle.dry_run.planned_count == 1
    assert bundle.execution_preview.ready is True
    assert bundle.execution_preview.executable_count == 1


def test_build_duplicate_workflow_from_scan_builds_unresolved_bundle_without_policy(tmp_path: Path) -> None:
    source_a = tmp_path / "source_a"
    source_b = tmp_path / "source_b"
    source_a.mkdir()
    source_b.mkdir()

    (source_a / "one.jpg").write_bytes(b"duplicate-bytes")
    (source_b / "two.jpg").write_bytes(b"duplicate-bytes")

    scan_result = scan_exact_duplicates(DuplicateScanConfig(source_dirs=[source_a, source_b]))
    bundle = build_duplicate_workflow_from_scan(scan_result, "delete")

    assert bundle.cleanup_plan.ready_for_dry_run is False
    assert bundle.dry_run.ready is False
    assert bundle.execution_preview.ready is False
    assert bundle.execution_preview.blocked_count == 2


def test_execute_duplicate_workflow_bundle_runs_execution_preview(tmp_path: Path) -> None:
    keep = tmp_path / "keep.jpg"
    remove = tmp_path / "remove.jpg"
    keep.write_bytes(b"same")
    remove.write_bytes(b"same")

    group = _group([keep, remove], file_size=4, digest="execute")
    decisions = build_duplicate_decisions([group], "first")
    bundle = build_duplicate_workflow_bundle([group], decisions, "delete")

    result = execute_duplicate_workflow_bundle(bundle, apply=False)

    assert result.processed_rows == 1
    assert result.executed_rows == 1
    assert result.error_rows == 0
    assert remove.exists()
