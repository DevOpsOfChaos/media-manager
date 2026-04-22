from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from media_manager.core.organizer import (
    DEFAULT_ORGANIZE_PATTERN,
    OrganizeDryRun,
    OrganizeExecutionResult,
    OrganizePlannerOptions,
    build_organize_dry_run,
    execute_organize_plan,
)
from media_manager.core.renamer import (
    RenameDryRun,
    RenameExecutionResult,
    RenamePlannerOptions,
    build_rename_dry_run,
    execute_rename_dry_run,
)
from media_manager.core.scanner import ScanOptions, ScanSummary, scan_media_sources
from media_manager.core.state import write_execution_journal
from media_manager.duplicate_workflow import (
    DuplicateWorkflowBundle,
    build_duplicate_decisions,
    build_duplicate_workflow_bundle,
)
from media_manager.duplicates import DuplicateScanConfig, DuplicateScanResult, scan_exact_duplicates

DEFAULT_CLEANUP_RENAME_TEMPLATE = "{date:%Y-%m-%d_%H-%M-%S}_{stem}"
CleanupDuplicatePolicy = Literal["first", "newest", "oldest"]
CleanupApplyStep = Literal["organize", "rename"]


@dataclass(slots=True, frozen=True)
class CleanupWorkflowOptions:
    source_dirs: tuple[Path, ...]
    target_root: Path
    organize_pattern: str = DEFAULT_ORGANIZE_PATTERN
    rename_template: str = DEFAULT_CLEANUP_RENAME_TEMPLATE
    recursive: bool = True
    include_hidden: bool = False
    follow_symlinks: bool = False
    duplicate_policy: CleanupDuplicatePolicy | None = None
    duplicate_mode: str = "copy"
    exiftool_path: Path | None = None
    include_associated_files: bool = False


@dataclass(slots=True)
class CleanupWorkflowReport:
    options: CleanupWorkflowOptions
    scan_summary: ScanSummary
    duplicate_scan_result: DuplicateScanResult
    duplicate_workflow: DuplicateWorkflowBundle
    organize_plan: OrganizeDryRun
    rename_dry_run: RenameDryRun

    @property
    def media_file_count(self) -> int:
        return self.scan_summary.media_file_count

    @property
    def missing_source_count(self) -> int:
        return len(self.scan_summary.missing_sources)

    @property
    def decisions_count(self) -> int:
        return len(self.duplicate_workflow.decisions)

    @property
    def media_group_count(self) -> int:
        return int(getattr(self.organize_plan, "media_group_count", len(self.organize_plan.entries)))

    @property
    def associated_file_count(self) -> int:
        return int(getattr(self.organize_plan, "associated_file_count", 0))

    @property
    def association_warning_count(self) -> int:
        return int(getattr(self.organize_plan, "association_warning_count", 0))

    @property
    def group_kind_summary(self) -> dict[str, int]:
        summary = getattr(self.organize_plan, "group_kind_summary", None)
        if summary is None:
            return {"single": len(self.organize_plan.entries)}
        return dict(sorted(summary.items()))

    @property
    def has_errors(self) -> bool:
        return any(
            [
                self.missing_source_count > 0,
                self.duplicate_scan_result.errors > 0,
                self.organize_plan.error_count > 0,
                self.rename_dry_run.error_count > 0,
            ]
        )


@dataclass(slots=True)
class CleanupExecutionReport:
    report: CleanupWorkflowReport
    apply_step: CleanupApplyStep
    organize_result: OrganizeExecutionResult | None = None
    rename_result: RenameExecutionResult | None = None
    journal_path: Path | None = None

    @property
    def error_count(self) -> int:
        if self.apply_step == "organize" and self.organize_result is not None:
            return self.organize_result.error_count
        if self.apply_step == "rename" and self.rename_result is not None:
            return self.rename_result.error_count
        return 0


def build_cleanup_workflow_report(options: CleanupWorkflowOptions) -> CleanupWorkflowReport:
    if options.duplicate_mode not in {"copy", "move", "delete"}:
        raise ValueError("Cleanup duplicate mode must be one of: copy, move, delete.")

    scan_summary = scan_media_sources(
        ScanOptions(
            source_dirs=options.source_dirs,
            recursive=options.recursive,
            include_hidden=options.include_hidden,
            follow_symlinks=options.follow_symlinks,
        )
    )

    duplicate_scan_result = scan_exact_duplicates(DuplicateScanConfig(source_dirs=list(options.source_dirs)))
    duplicate_decisions: dict[str, str] = {}
    if options.duplicate_policy is not None:
        duplicate_decisions = build_duplicate_decisions(
            duplicate_scan_result.exact_groups,
            options.duplicate_policy,
        )

    duplicate_target_root = options.target_root if options.duplicate_mode in {"copy", "move"} else None
    duplicate_workflow = build_duplicate_workflow_bundle(
        duplicate_scan_result.exact_groups,
        duplicate_decisions,
        options.duplicate_mode,
        target_root=duplicate_target_root,
    )

    organize_plan = build_organize_dry_run(
        OrganizePlannerOptions(
            source_dirs=options.source_dirs,
            target_root=options.target_root,
            pattern=options.organize_pattern,
            recursive=options.recursive,
            include_hidden=options.include_hidden,
            follow_symlinks=options.follow_symlinks,
            operation_mode="copy",
            exiftool_path=options.exiftool_path,
            include_associated_files=options.include_associated_files,
        )
    )

    rename_dry_run = build_rename_dry_run(
        RenamePlannerOptions(
            source_dirs=options.source_dirs,
            template=options.rename_template,
            recursive=options.recursive,
            include_hidden=options.include_hidden,
            follow_symlinks=options.follow_symlinks,
            exiftool_path=options.exiftool_path,
            include_associated_files=options.include_associated_files,
        )
    )

    return CleanupWorkflowReport(
        options=options,
        scan_summary=scan_summary,
        duplicate_scan_result=duplicate_scan_result,
        duplicate_workflow=duplicate_workflow,
        organize_plan=organize_plan,
        rename_dry_run=rename_dry_run,
    )


def _build_organize_journal_entries(result: OrganizeExecutionResult) -> list[dict[str, object]]:
    entries: list[dict[str, object]] = []
    for item in result.entries:
        target_path = item.target_path
        plan_entry = getattr(item, "plan_entry", None)
        entry = {
            "source_path": str(item.source_path),
            "target_path": None if target_path is None else str(target_path),
            "action": item.outcome,
            "reason": item.reason,
            "reversible": item.outcome in {"copied", "moved"},
            "undo_action": None,
            "undo_source_path": None,
            "undo_target_path": None,
            "group_id": getattr(plan_entry, "group_id", None),
            "group_kind": getattr(plan_entry, "group_kind", None),
            "main_file": None if plan_entry is None else str(plan_entry.source_path),
            "associated_files": [] if plan_entry is None else [str(path) for path in getattr(plan_entry, "associated_paths", ())],
        }
        if item.outcome == "copied" and target_path is not None:
            entry["undo_action"] = "delete_target"
            entry["undo_target_path"] = str(target_path)
        elif item.outcome == "moved" and target_path is not None:
            entry["undo_action"] = "move_back"
            entry["undo_source_path"] = str(target_path)
            entry["undo_target_path"] = str(item.source_path)
        entries.append(entry)
    return entries


def _build_rename_journal_entries(result: RenameExecutionResult) -> list[dict[str, object]]:
    entries: list[dict[str, object]] = []
    for item in result.entries:
        plan_entry = getattr(item, "plan_entry", None)
        member_results = getattr(item, "member_results", ()) or ()
        if member_results:
            for member in member_results:
                reversible = member.action == "renamed" and member.target_path is not None
                entries.append(
                    {
                        "source_path": str(member.source_path),
                        "target_path": None if member.target_path is None else str(member.target_path),
                        "action": member.action,
                        "reason": member.reason,
                        "reversible": reversible,
                        "undo_action": "rename_back" if reversible else None,
                        "undo_source_path": str(member.target_path) if reversible and member.target_path is not None else None,
                        "undo_target_path": str(member.source_path) if reversible else None,
                        "group_id": getattr(plan_entry, "group_id", None),
                        "group_kind": getattr(plan_entry, "group_kind", None),
                        "main_file": None if plan_entry is None else str(plan_entry.source_path),
                        "associated_files": [] if plan_entry is None else [str(path) for path in getattr(plan_entry, "associated_paths", ())],
                    }
                )
            continue

        entry = {
            "source_path": str(item.source_path),
            "target_path": None if item.target_path is None else str(item.target_path),
            "action": item.action,
            "reason": item.reason,
            "reversible": item.action == "renamed" and item.target_path is not None,
            "undo_action": None,
            "undo_source_path": None,
            "undo_target_path": None,
            "group_id": getattr(plan_entry, "group_id", None),
            "group_kind": getattr(plan_entry, "group_kind", None),
            "main_file": None if plan_entry is None else str(plan_entry.source_path),
            "associated_files": [] if plan_entry is None else [str(path) for path in getattr(plan_entry, "associated_paths", ())],
        }
        if item.action == "renamed" and item.target_path is not None:
            entry["undo_action"] = "rename_back"
            entry["undo_source_path"] = str(item.target_path)
            entry["undo_target_path"] = str(item.source_path)
        entries.append(entry)
    return entries


def execute_cleanup_workflow(
    report: CleanupWorkflowReport,
    *,
    apply_step: CleanupApplyStep,
    journal_path: str | Path | None = None,
) -> CleanupExecutionReport:
    if apply_step == "organize":
        organize_result = execute_organize_plan(report.organize_plan)
        execution_report = CleanupExecutionReport(
            report=report,
            apply_step=apply_step,
            organize_result=organize_result,
        )
        if journal_path is not None:
            write_execution_journal(
                journal_path,
                command_name="cleanup-organize",
                apply_requested=True,
                exit_code=0 if organize_result.error_count == 0 else 1,
                entries=_build_organize_journal_entries(organize_result),
            )
            execution_report.journal_path = Path(journal_path)
        return execution_report

    if apply_step == "rename":
        rename_result = execute_rename_dry_run(report.rename_dry_run, apply=True)
        execution_report = CleanupExecutionReport(
            report=report,
            apply_step=apply_step,
            rename_result=rename_result,
        )
        if journal_path is not None:
            write_execution_journal(
                journal_path,
                command_name="cleanup-rename",
                apply_requested=True,
                exit_code=0 if rename_result.error_count == 0 else 1,
                entries=_build_rename_journal_entries(rename_result),
            )
            execution_report.journal_path = Path(journal_path)
        return execution_report

    raise ValueError("Cleanup apply step must be either 'organize' or 'rename'.")
