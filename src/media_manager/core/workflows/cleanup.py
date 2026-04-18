from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from media_manager.core.organizer import (
    DEFAULT_ORGANIZE_PATTERN,
    OrganizeDryRun,
    OrganizePlannerOptions,
    build_organize_dry_run,
)
from media_manager.core.renamer import RenameDryRun, RenamePlannerOptions, build_rename_dry_run
from media_manager.core.scanner import ScanOptions, ScanSummary, scan_media_sources
from media_manager.duplicate_workflow import (
    DuplicateWorkflowBundle,
    build_duplicate_decisions,
    build_duplicate_workflow_bundle,
)
from media_manager.duplicates import DuplicateScanConfig, DuplicateScanResult, scan_exact_duplicates

DEFAULT_CLEANUP_RENAME_TEMPLATE = "{date:%Y-%m-%d_%H-%M-%S}_{stem}"
CleanupDuplicatePolicy = Literal["first", "newest", "oldest"]


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
    def has_errors(self) -> bool:
        return any(
            [
                self.missing_source_count > 0,
                self.duplicate_scan_result.errors > 0,
                self.organize_plan.error_count > 0,
                self.rename_dry_run.error_count > 0,
            ]
        )


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
