from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from .cleanup_plan import ExactCleanupDryRun, ExactCleanupPlan, build_exact_cleanup_dry_run, build_exact_cleanup_plan, build_exact_group_id
from .duplicates import DuplicateScanResult, ExactDuplicateGroup
from .execution_plan import DuplicateExecutionPreview, build_duplicate_execution_preview
from .execution_runner import DuplicateExecutionRunResult, run_duplicate_execution_preview

KeepPolicy = Literal["first", "newest", "oldest"]


@dataclass(slots=True)
class DuplicateWorkflowBundle:
    decisions: dict[str, str]
    cleanup_plan: ExactCleanupPlan
    dry_run: ExactCleanupDryRun
    execution_preview: DuplicateExecutionPreview



def choose_keep_path(group: ExactDuplicateGroup, policy: KeepPolicy) -> Path:
    if not group.files:
        raise ValueError("Exact duplicate group must contain at least one file")

    if policy == "first":
        return group.files[0]

    dated_paths: list[tuple[float, Path]] = []
    for path in group.files:
        try:
            timestamp = path.stat().st_mtime
        except OSError:
            timestamp = 0.0
        dated_paths.append((timestamp, path))

    if policy == "newest":
        return max(dated_paths, key=lambda item: (item[0], str(item[1]).lower()))[1]
    if policy == "oldest":
        return min(dated_paths, key=lambda item: (item[0], str(item[1]).lower()))[1]

    raise ValueError(f"Unsupported keep policy: {policy}")



def build_duplicate_decisions(exact_groups: list[ExactDuplicateGroup], policy: KeepPolicy) -> dict[str, str]:
    decisions: dict[str, str] = {}
    for group in exact_groups:
        keep_path = choose_keep_path(group, policy)
        decisions[build_exact_group_id(group)] = str(keep_path)
    return decisions



def build_duplicate_workflow_bundle(
    exact_groups: list[ExactDuplicateGroup],
    decisions: dict[str, str],
    operation_mode: str,
    target_root: str | Path | None = None,
) -> DuplicateWorkflowBundle:
    cleanup_plan = build_exact_cleanup_plan(exact_groups, decisions, operation_mode)
    dry_run = build_exact_cleanup_dry_run(exact_groups, decisions, operation_mode, target_root=target_root)
    execution_preview = build_duplicate_execution_preview(dry_run)
    return DuplicateWorkflowBundle(
        decisions=dict(decisions),
        cleanup_plan=cleanup_plan,
        dry_run=dry_run,
        execution_preview=execution_preview,
    )



def build_duplicate_workflow_from_scan(
    scan_result: DuplicateScanResult,
    operation_mode: str,
    *,
    decision_policy: KeepPolicy | None = None,
    target_root: str | Path | None = None,
) -> DuplicateWorkflowBundle:
    decisions: dict[str, str] = {}
    if decision_policy is not None:
        decisions = build_duplicate_decisions(scan_result.exact_groups, decision_policy)
    return build_duplicate_workflow_bundle(
        scan_result.exact_groups,
        decisions,
        operation_mode,
        target_root=target_root,
    )



def execute_duplicate_workflow_bundle(
    bundle: DuplicateWorkflowBundle,
    *,
    apply: bool = False,
) -> DuplicateExecutionRunResult:
    return run_duplicate_execution_preview(bundle.execution_preview, apply=apply)
