from pathlib import Path

from media_manager.cleanup_plan import build_exact_cleanup_plan, build_exact_group_id
from media_manager.duplicates import ExactDuplicateGroup


def _group(paths: list[str], file_size: int, full_digest: str) -> ExactDuplicateGroup:
    return ExactDuplicateGroup(
        files=[Path(path) for path in paths],
        file_size=file_size,
        sample_digest="sample",
        full_digest=full_digest,
        same_name=False,
        same_suffix=True,
    )


def test_build_exact_cleanup_plan_marks_unresolved_groups() -> None:
    groups = [
        _group([
            "/library/a/photo1.jpg",
            "/library/b/photo1.jpg",
        ], 1000, "hash-a"),
    ]

    plan = build_exact_cleanup_plan(groups, decisions={}, operation_mode="copy")

    assert plan.total_groups == 1
    assert plan.resolved_groups == 0
    assert plan.unresolved_groups == 1
    assert plan.duplicate_files == 2
    assert plan.extra_duplicates == 1
    assert plan.estimated_reclaimable_bytes == 0
    assert len(plan.planned_removals) == 0
    assert len(plan.unresolved) == 1
    assert not plan.ready_for_dry_run


def test_build_exact_cleanup_plan_creates_removal_candidates_for_resolved_groups() -> None:
    group = _group([
        "/library/a/photo1.jpg",
        "/library/b/photo1.jpg",
        "/library/c/photo1.jpg",
    ], 2048, "hash-b")
    group_id = build_exact_group_id(group)

    plan = build_exact_cleanup_plan(
        [group],
        decisions={group_id: "/library/b/photo1.jpg"},
        operation_mode="move",
    )

    assert plan.total_groups == 1
    assert plan.resolved_groups == 1
    assert plan.unresolved_groups == 0
    assert plan.duplicate_files == 3
    assert plan.extra_duplicates == 2
    assert plan.estimated_reclaimable_bytes == 4096
    assert len(plan.planned_removals) == 2
    assert {str(item.remove_path) for item in plan.planned_removals} == {
        "/library/a/photo1.jpg",
        "/library/c/photo1.jpg",
    }
    assert all(item.operation_mode == "move" for item in plan.planned_removals)
    assert plan.ready_for_dry_run


def test_build_exact_cleanup_plan_treats_invalid_keep_target_as_unresolved() -> None:
    group = _group([
        "/library/a/photo2.jpg",
        "/library/b/photo2.jpg",
    ], 512, "hash-c")
    group_id = build_exact_group_id(group)

    plan = build_exact_cleanup_plan(
        [group],
        decisions={group_id: "/library/z/does_not_exist.jpg"},
        operation_mode="delete",
    )

    assert plan.resolved_groups == 0
    assert plan.unresolved_groups == 1
    assert len(plan.planned_removals) == 0
    assert plan.estimated_reclaimable_bytes == 0
