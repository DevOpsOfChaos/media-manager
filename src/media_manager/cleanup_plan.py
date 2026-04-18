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


@dataclass(slots=True)
class DryRunAction:
    action_type: str
    group_id: str
    operation_mode: str
    source_path: Path
    survivor_path: Path | None
    file_size: int
    reason: str
    status: str
    target_path: Path | None = None


@dataclass(slots=True)
class ExactCleanupDryRun:
    ready: bool
    planned_actions: list[DryRunAction] = field(default_factory=list)
    blocked_actions: list[DryRunAction] = field(default_factory=list)

    @property
    def total_rows(self) -> int:
        return len(self.planned_actions) + len(self.blocked_actions)

    @property
    def planned_count(self) -> int:
        return len(self.planned_actions)

    @property
    def blocked_count(self) -> int:
        return len(self.blocked_actions)

    @property
    def delete_count(self) -> int:
        return sum(1 for row in self.planned_actions if row.action_type == "delete")

    @property
    def exclude_from_copy_count(self) -> int:
        return sum(1 for row in self.planned_actions if row.action_type == "exclude_from_copy")

    @property
    def exclude_from_move_count(self) -> int:
        return sum(1 for row in self.planned_actions if row.action_type == "exclude_from_move")


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


def _action_type_for_operation_mode(operation_mode: str) -> str:
    if operation_mode == "delete":
        return "delete"
    if operation_mode == "move":
        return "exclude_from_move"
    return "exclude_from_copy"


def _target_path_for_remove_candidate(
    operation_mode: str,
    survivor_path: Path,
    remove_path: Path,
    target_root: Path | None,
) -> Path | None:
    if operation_mode == "delete":
        return None

    if target_root is None:
        return survivor_path

    try:
        relative_name = remove_path.name
    except Exception:
        relative_name = survivor_path.name

    return target_root / relative_name


def build_exact_cleanup_dry_run(
    exact_groups: Iterable[ExactDuplicateGroup],
    decisions: dict[str, str],
    operation_mode: str,
    target_root: str | Path | None = None,
) -> ExactCleanupDryRun:
    plan = build_exact_cleanup_plan(exact_groups, decisions, operation_mode)
    target_root_path = Path(target_root) if target_root else None
    dry_run = ExactCleanupDryRun(ready=plan.ready_for_dry_run)

    action_type = _action_type_for_operation_mode(operation_mode)

    for item in plan.planned_removals:
        dry_run.planned_actions.append(
            DryRunAction(
                action_type=action_type,
                group_id=item.group_id,
                operation_mode=item.operation_mode,
                source_path=item.remove_path,
                survivor_path=item.keep_path,
                file_size=item.file_size,
                reason=item.reason,
                status="planned",
                target_path=_target_path_for_remove_candidate(
                    item.operation_mode,
                    item.keep_path,
                    item.remove_path,
                    target_root_path,
                ),
            )
        )

    for unresolved in plan.unresolved:
        for candidate in unresolved.candidate_paths:
            dry_run.blocked_actions.append(
                DryRunAction(
                    action_type="blocked_exact_group",
                    group_id=unresolved.group_id,
                    operation_mode=operation_mode,
                    source_path=candidate,
                    survivor_path=None,
                    file_size=unresolved.file_size,
                    reason="missing_keep_decision",
                    status="blocked",
                    target_path=None,
                )
            )

    return dry_run
