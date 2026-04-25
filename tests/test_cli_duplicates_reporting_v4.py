from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

from media_manager.cli_duplicates import _build_json_report_payload, main
from media_manager.cleanup_plan import UnresolvedExactGroup
from media_manager.duplicates import ExactDuplicateGroup
from media_manager.execution_plan import ExecutionPreviewRow


def _group(tmp_path: Path, name_a: str = "keep.jpg", name_b: str = "remove.jpg", digest: str = "digest") -> ExactDuplicateGroup:
    a = tmp_path / name_a
    b = tmp_path / name_b
    a.write_bytes(b"same")
    b.write_bytes(b"same")
    return ExactDuplicateGroup(
        files=[a, b],
        file_size=4,
        sample_digest="sample",
        full_digest=digest,
        same_name=False,
        same_suffix=True,
    )


def test_duplicate_json_payload_includes_outcome_review_and_filters(tmp_path: Path) -> None:
    group = _group(tmp_path)
    scan_result = SimpleNamespace(
        scanned_files=2,
        size_candidate_files=2,
        hashed_files=2,
        exact_groups=[group],
        exact_duplicate_files=2,
        exact_duplicates=1,
        errors=0,
        size_group_errors=0,
        sample_errors=0,
        hash_errors=0,
        compare_errors=0,
        skipped_filtered_files=3,
    )
    bundle = SimpleNamespace(
        decisions={},
        cleanup_plan=SimpleNamespace(
            total_groups=1,
            resolved_groups=0,
            unresolved_groups=1,
            unresolved=[UnresolvedExactGroup(group_id="g1", candidate_paths=group.files, file_size=4)],
            planned_removals=[],
            estimated_reclaimable_bytes=0,
        ),
        dry_run=SimpleNamespace(
            ready=False,
            planned_count=0,
            blocked_count=2,
            delete_count=0,
            exclude_from_copy_count=0,
            exclude_from_move_count=0,
            planned_actions=[],
            blocked_actions=[],
        ),
        execution_preview=SimpleNamespace(
            ready=False,
            executable_count=0,
            deferred_count=0,
            blocked_count=1,
            delete_count=0,
            rows=[ExecutionPreviewRow("blocked", "blocked", "g1", "delete", group.files[0], None, None, 4, "missing_keep_decision")],
        ),
    )

    payload = _build_json_report_payload(
        scan_result,
        bundle,
        None,
        mode="delete",
        include_patterns=("*.jpg",),
        exclude_patterns=("*edited*",),
    )

    assert payload["command"] == "duplicates"
    assert payload["mode"] == "delete"
    assert payload["include_patterns"] == ["*.jpg"]
    assert payload["exclude_patterns"] == ["*edited*"]
    assert payload["scan"]["skipped_filtered_files"] == 3
    assert payload["summary"]["unresolved_group_count"] == 1
    assert payload["outcome_report"]["status"] == "review_required"
    assert payload["review"]["candidate_count"] >= 1


def test_cli_duplicates_writes_report_and_review_json_with_new_aliases(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    first = source / "a.jpg"
    second = source / "b.jpg"
    first.write_bytes(b"same")
    second.write_bytes(b"same")

    report_path = tmp_path / "reports" / "duplicates.json"
    review_path = tmp_path / "reports" / "duplicates-review.json"

    code = main([
        "--source", str(source),
        "--policy", "first",
        "--mode", "delete",
        "--report-json", str(report_path),
        "--review-json", str(review_path),
        "--include-pattern", "*.jpg",
    ])

    assert code == 0
    report = json.loads(report_path.read_text(encoding="utf-8"))
    review = json.loads(review_path.read_text(encoding="utf-8"))
    assert report["outcome_report"]["status"] == "delete_preview_ready"
    assert report["summary"]["exact_group_count"] == 1
    assert report["include_patterns"] == ["*.jpg"]
    assert review["command"] == "duplicates"
    assert "review" in review
