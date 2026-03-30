from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

from .duplicates import ExactDuplicateGroup


@dataclass(slots=True)
class PlannedRemoval:
    group_id: str
    keep_path: Path
    remove_path: Path
    file_size: int
    operation_mode: str
    reason: str = "exact_duplicate_remove_candidate"


@dataclass(slots=True)
class UnresolvedExactGroup:
    group_id: str
    candidate_paths: list[Path] = field(default_factory=list)
    file_size: int = 0


@dataclass(slots=True)
class ExactCleanupPlan:
    total_groups: int = 0
    resolved_groups: int = 0
    unresolved_groups: int = 0
    duplicate_files: int = 0
    extra_duplicates: int = 0
    estimated_reclaimable_bytes: int = 0
    planned_removals: list[PlannedRemoval] = field(default_factory=list)
    unresolved: list[UnresolvedExactGroup] = field(default_factory=list)

    @property
    def ready_for_dry_run(self) -> bool:
        if self.total_groups == 0:
            return True
        return self.unresolved_groups == 0


def build_exact_group_id(group: ExactDuplicateGroup) -> str:
    return f"{group.file_size}:{group.full_digest}"


def build_exact_cleanup_plan(
    exact_groups: Iterable[ExactDuplicateGroup],
    decisions: dict[str, str],
    operation_mode: str,
) -> ExactCleanupPlan:
    plan = ExactCleanupPlan()

    for group in exact_groups:
        group_id = build_exact_group_id(group)
        plan.total_groups += 1
        plan.duplicate_files += len(group.files)
        plan.extra_duplicates += max(0, len(group.files) - 1)

        keep_path_str = decisions.get(group_id, "")
        keep_path = Path(keep_path_str) if keep_path_str else None

        if keep_path is None or keep_path not in group.files:
            plan.unresolved_groups += 1
            plan.unresolved.append(
                UnresolvedExactGroup(
                    group_id=group_id,
                    candidate_paths=list(group.files),
                    file_size=group.file_size,
                )
            )
            continue

        plan.resolved_groups += 1
        for path in group.files:
            if path == keep_path:
                continue
            plan.planned_removals.append(
                PlannedRemoval(
                    group_id=group_id,
                    keep_path=keep_path,
                    remove_path=path,
                    file_size=group.file_size,
                    operation_mode=operation_mode,
                )
            )
            plan.estimated_reclaimable_bytes += group.file_size

    return plan
