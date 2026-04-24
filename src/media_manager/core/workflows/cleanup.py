from __future__ import annotations

from dataclasses import dataclass, field
import os
from pathlib import Path
import shutil
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
CleanupLeftoverMode = Literal["off", "consolidate"]


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
    leftover_mode: CleanupLeftoverMode = "off"
    leftover_dir_name: str = "_remaining_files"


@dataclass(slots=True, frozen=True)
class CleanupLeftoverEntry:
    source_root: Path
    source_path: Path
    target_path: Path
    conflict_resolved: bool = False


@dataclass(slots=True)
class CleanupLeftoverResult:
    requested: bool
    mode: CleanupLeftoverMode
    directory_name: str
    entries: list[CleanupLeftoverEntry] = field(default_factory=list)
    removed_empty_directories: list[Path] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def file_count(self) -> int:
        return len(self.entries)

    @property
    def removed_empty_directory_count(self) -> int:
        return len(self.removed_empty_directories)

    @property
    def conflict_count(self) -> int:
        return sum(1 for item in self.entries if item.conflict_resolved)

    @property
    def error_count(self) -> int:
        return len(self.errors)


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
        value = int(getattr(self.organize_plan, "media_group_count", 0))
        if value > 0 or not self.organize_plan.entries:
            return value
        return len(self.organize_plan.entries)

    @property
    def associated_file_count(self) -> int:
        return int(getattr(self.organize_plan, "associated_file_count", 0))

    @property
    def association_warning_count(self) -> int:
        return int(getattr(self.organize_plan, "association_warning_count", 0))

    @property
    def group_kind_summary(self) -> dict[str, int]:
        summary = dict(getattr(self.organize_plan, "group_kind_summary", {}))
        if summary or not self.organize_plan.entries:
            return dict(sorted(summary.items()))
        return {"single": len(self.organize_plan.entries)}

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
    leftover_result: CleanupLeftoverResult | None = None

    @property
    def error_count(self) -> int:
        base = 0
        if self.apply_step == "organize" and self.organize_result is not None:
            base = self.organize_result.error_count
        elif self.apply_step == "rename" and self.rename_result is not None:
            base = self.rename_result.error_count
        if self.leftover_result is not None:
            base += self.leftover_result.error_count
        return base


def _validate_leftover_dir_name(name: str) -> None:
    text = str(name).strip()
    if text in {"", ".", ".."}:
        raise ValueError("Cleanup leftover directory name must not be empty or relative navigation.")
    if "/" in text or "\\" in text:
        raise ValueError("Cleanup leftover directory name must be a single directory segment.")


def _normalized_path_key(path: Path) -> str:
    return os.path.normcase(str(path))


def build_cleanup_workflow_report(options: CleanupWorkflowOptions) -> CleanupWorkflowReport:
    if options.duplicate_mode not in {"copy", "move", "delete"}:
        raise ValueError("Cleanup duplicate mode must be one of: copy, move, delete.")
    if options.leftover_mode not in {"off", "consolidate"}:
        raise ValueError("Cleanup leftover mode must be one of: off, consolidate.")
    _validate_leftover_dir_name(options.leftover_dir_name)

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


def _journal_group_fields(plan_entry) -> dict[str, object]:
    return {
        "group_id": getattr(plan_entry, "group_id", None),
        "group_kind": getattr(plan_entry, "group_kind", None),
        "main_file": None if plan_entry is None else str(plan_entry.source_path),
        "associated_files": [] if plan_entry is None else [str(path) for path in getattr(plan_entry, "associated_paths", ())],
    }


def _build_organize_journal_entries(
    result: OrganizeExecutionResult,
    leftover_result: CleanupLeftoverResult | None = None,
) -> list[dict[str, object]]:
    entries: list[dict[str, object]] = []
    for item in result.entries:
        plan_entry = getattr(item, "plan_entry", None)
        member_results = getattr(item, "member_results", ()) or ()
        if member_results:
            for member in member_results:
                outcome = getattr(member, "outcome", None)
                reversible = outcome in {"copied", "moved"}
                undo_action = None
                undo_from_path = None
                undo_to_path = None
                if outcome == "copied" and member.target_path is not None:
                    undo_action = "delete_target"
                    undo_from_path = str(member.target_path)
                elif outcome == "moved" and member.target_path is not None:
                    undo_action = "move_back"
                    undo_from_path = str(member.target_path)
                    undo_to_path = str(member.source_path)
                entries.append(
                    {
                        "source_path": str(member.source_path),
                        "target_path": None if member.target_path is None else str(member.target_path),
                        "outcome": outcome,
                        "reason": member.reason,
                        "reversible": reversible,
                        "undo_action": undo_action,
                        "undo_from_path": undo_from_path,
                        "undo_to_path": undo_to_path,
                        "role": getattr(member, "role", None),
                        "is_main_file": bool(getattr(member, "is_main_file", getattr(member, "role", None) == "main")),
                        **_journal_group_fields(plan_entry),
                    }
                )
            continue

        target_path = item.target_path
        entry = {
            "source_path": str(item.source_path),
            "target_path": None if target_path is None else str(target_path),
            "outcome": item.outcome,
            "reason": item.reason,
            "reversible": item.outcome in {"copied", "moved"},
            "undo_action": None,
            "undo_from_path": None,
            "undo_to_path": None,
            **_journal_group_fields(plan_entry),
        }
        if item.outcome == "copied" and target_path is not None:
            entry["undo_action"] = "delete_target"
            entry["undo_from_path"] = str(target_path)
        elif item.outcome == "moved" and target_path is not None:
            entry["undo_action"] = "move_back"
            entry["undo_from_path"] = str(target_path)
            entry["undo_to_path"] = str(item.source_path)
        entries.append(entry)

    if leftover_result is not None:
        for item in leftover_result.entries:
            entries.append(
                {
                    "source_path": str(item.source_path),
                    "target_path": str(item.target_path),
                    "outcome": "leftover-consolidated",
                    "reason": "moved source leftover into the cleanup leftover directory",
                    "reversible": True,
                    "undo_action": "move_back",
                    "undo_from_path": str(item.target_path),
                    "undo_to_path": str(item.source_path),
                    "leftover_consolidation": True,
                    "source_root": str(item.source_root),
                    "associated_files": [],
                }
            )
    return entries


def _build_rename_journal_entries(result: RenameExecutionResult) -> list[dict[str, object]]:
    entries: list[dict[str, object]] = []
    for item in result.entries:
        plan_entry = getattr(item, "plan_entry", None)
        member_results = getattr(item, "member_results", ()) or ()
        if member_results:
            for member in member_results:
                outcome = getattr(member, "action", getattr(member, "outcome", None))
                reversible = outcome == "renamed" and member.target_path is not None
                entries.append(
                    {
                        "source_path": str(member.source_path),
                        "target_path": None if member.target_path is None else str(member.target_path),
                        "outcome": outcome,
                        "reason": member.reason,
                        "reversible": reversible,
                        "undo_action": "rename_back" if reversible else None,
                        "undo_from_path": None if not reversible else str(member.target_path),
                        "undo_to_path": None if not reversible else str(member.source_path),
                        "role": getattr(member, "role", None),
                        "is_main_file": bool(getattr(member, "is_main_file", getattr(member, "role", None) == "main")),
                        **_journal_group_fields(plan_entry),
                    }
                )
            continue

        reversible = item.action == "renamed" and item.target_path is not None
        entries.append(
            {
                "source_path": str(item.source_path),
                "target_path": None if item.target_path is None else str(item.target_path),
                "outcome": item.action,
                "reason": item.reason,
                "reversible": reversible,
                "undo_action": "rename_back" if reversible else None,
                "undo_from_path": None if not reversible else str(item.target_path),
                "undo_to_path": None if not reversible else str(item.source_path),
                **_journal_group_fields(plan_entry),
            }
        )
    return entries


def _iter_leftover_files(source_root: Path, leftover_dir: Path) -> list[Path]:
    files: list[Path] = []
    if not source_root.exists():
        return files
    for current_root, dirnames, filenames in os.walk(source_root, topdown=True):
        current_root_path = Path(current_root)
        if current_root_path == leftover_dir:
            dirnames[:] = []
            continue
        visible_dirnames: list[str] = []
        for dirname in dirnames:
            candidate_dir = current_root_path / dirname
            if _normalized_path_key(candidate_dir).startswith(_normalized_path_key(leftover_dir)):
                continue
            visible_dirnames.append(dirname)
        dirnames[:] = visible_dirnames
        for filename in sorted(filenames):
            candidate = current_root_path / filename
            if _normalized_path_key(candidate).startswith(_normalized_path_key(leftover_dir)):
                continue
            if candidate.is_file():
                files.append(candidate)
    files.sort(key=lambda item: (_normalized_path_key(item.parent), _normalized_path_key(item)))
    return files


def _next_leftover_target(leftover_dir: Path, file_name: str) -> tuple[Path, bool]:
    candidate = leftover_dir / file_name
    if not candidate.exists():
        return candidate, False

    path_obj = Path(file_name)
    stem = path_obj.stem
    suffix = path_obj.suffix
    index = 2
    while True:
        candidate = leftover_dir / f"{stem}__{index}{suffix}"
        if not candidate.exists():
            return candidate, True
        index += 1


def _remove_empty_directories(source_root: Path, leftover_dir: Path) -> list[Path]:
    removed: list[Path] = []
    for current_root, dirnames, filenames in os.walk(source_root, topdown=False):
        current_root_path = Path(current_root)
        if current_root_path == source_root:
            continue
        if current_root_path == leftover_dir:
            continue
        if _normalized_path_key(current_root_path).startswith(_normalized_path_key(leftover_dir)):
            continue
        if dirnames or filenames:
            continue
        try:
            current_root_path.rmdir()
        except OSError:
            continue
        removed.append(current_root_path)
    removed.sort(key=lambda item: _normalized_path_key(item))
    return removed


def _consolidate_leftovers(report: CleanupWorkflowReport) -> CleanupLeftoverResult:
    result = CleanupLeftoverResult(
        requested=True,
        mode=report.options.leftover_mode,
        directory_name=report.options.leftover_dir_name,
    )
    for source_root in report.options.source_dirs:
        leftover_dir = source_root / report.options.leftover_dir_name
        candidate_files = _iter_leftover_files(source_root, leftover_dir)
        if not candidate_files:
            continue
        for candidate in candidate_files:
            try:
                leftover_dir.mkdir(parents=True, exist_ok=True)
                target_path, conflict_resolved = _next_leftover_target(leftover_dir, candidate.name)
                shutil.move(str(candidate), str(target_path))
                result.entries.append(
                    CleanupLeftoverEntry(
                        source_root=source_root,
                        source_path=candidate,
                        target_path=target_path,
                        conflict_resolved=conflict_resolved,
                    )
                )
            except Exception as exc:  # pragma: no cover
                result.errors.append(str(exc))
        result.removed_empty_directories.extend(_remove_empty_directories(source_root, leftover_dir))
    return result


def execute_cleanup_workflow(
    report: CleanupWorkflowReport,
    *,
    apply_step: CleanupApplyStep,
    journal_path: str | Path | None = None,
) -> CleanupExecutionReport:
    if report.options.leftover_mode == "consolidate" and apply_step != "organize":
        raise ValueError("Cleanup leftover consolidation is currently only supported with apply_step='organize'.")

    if apply_step == "organize":
        organize_result = execute_organize_plan(report.organize_plan)
        leftover_result = None
        if (
            report.options.leftover_mode == "consolidate"
            and organize_result.error_count == 0
            and organize_result.conflict_count == 0
        ):
            leftover_result = _consolidate_leftovers(report)
        execution_report = CleanupExecutionReport(
            report=report,
            apply_step=apply_step,
            organize_result=organize_result,
            leftover_result=leftover_result,
        )
        if journal_path is not None:
            write_execution_journal(
                journal_path,
                command_name="cleanup-organize",
                apply_requested=True,
                exit_code=0 if execution_report.error_count == 0 else 1,
                entries=_build_organize_journal_entries(organize_result, leftover_result),
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
                exit_code=0 if execution_report.error_count == 0 else 1,
                entries=_build_rename_journal_entries(rename_result),
            )
            execution_report.journal_path = Path(journal_path)
        return execution_report

    raise ValueError("Cleanup apply step must be either 'organize' or 'rename'.")
