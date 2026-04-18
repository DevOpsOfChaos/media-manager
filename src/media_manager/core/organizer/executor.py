from __future__ import annotations

import shutil

from .models import OrganizeDryRun, OrganizeExecutionEntry, OrganizeExecutionResult


def execute_organize_plan(plan: OrganizeDryRun) -> OrganizeExecutionResult:
    result = OrganizeExecutionResult(plan=plan)

    for entry in plan.entries:
        if entry.status == "skipped":
            result.entries.append(OrganizeExecutionEntry(plan_entry=entry, outcome="skipped", reason=entry.reason))
            continue

        if entry.status == "conflict":
            result.entries.append(OrganizeExecutionEntry(plan_entry=entry, outcome="conflict", reason=entry.reason))
            continue

        if entry.status == "error":
            result.entries.append(OrganizeExecutionEntry(plan_entry=entry, outcome="error", reason=entry.reason))
            continue

        if entry.target_path is None:
            result.entries.append(OrganizeExecutionEntry(plan_entry=entry, outcome="error", reason="missing target path"))
            continue

        try:
            entry.target_path.parent.mkdir(parents=True, exist_ok=True)
            if entry.operation_mode == "move":
                shutil.move(str(entry.source_path), str(entry.target_path))
                outcome = "moved"
            else:
                shutil.copy2(str(entry.source_path), str(entry.target_path))
                outcome = "copied"
            result.entries.append(OrganizeExecutionEntry(plan_entry=entry, outcome=outcome, reason="executed organize action"))
        except Exception as exc:  # pragma: no cover
            result.entries.append(OrganizeExecutionEntry(plan_entry=entry, outcome="error", reason=str(exc)))

    return result
