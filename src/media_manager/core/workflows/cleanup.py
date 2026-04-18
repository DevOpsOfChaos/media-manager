
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from media_manager.core.organizer import (
    DEFAULT_ORGANIZE_PATTERN,
    OrganizeDryRun,
    OrganizePlannerOptions,
    build_organize_dry_run,
)
from media_manager.core.renamer import (
    RenameDryRun,
    RenamePlannerOptions,
    build_rename_dry_run,
)
from media_manager.duplicate_workflow import (
    DuplicateWorkflowBundle,
    build_duplicate_decisions,
    build_duplicate_workflow_bundle,
)
from media_manager.duplicates import DuplicateScanConfig, DuplicateScanResult, scan_exact_duplicates

DEFAULT_CLEANUP_RENAME_TEMPLATE = "{date:%Y-%m-%d_%H-%M-%S}_{stem}"


@dataclass(slots=True, frozen=True)
class CleanupWorkflowOptions:
    source_dirs: tuple[Path, ...]
    target_root: Path
    organize_pattern: str = DEFAULT_ORGANIZE_PATTERN
    rename_template: str = DEFAULT_CLEANUP_RENAME_TEMPLATE
    duplicate_policy: str | None = None
    duplicate_mode: str = "copy"
    recursive: bool = True
    include_hidden: bool = False
    exiftool_path: Path | None = None


@dataclass(slots=True)
class CleanupDryRun:
    options: CleanupWorkflowOptions
    duplicate_scan: DuplicateScanResult
    duplicate_bundle: DuplicateWorkflowBundle
    organize_plan: OrganizeDryRun
    rename_plan: RenameDryRun

    @property
    def missing_source_count(self) -> int:
        missing: set[str] = set()
        for collection in (
            self.organize_plan.scan_summary.missing_sources,
            self.rename_plan.scan_summary.missing_sources,
        ):
            missing.update(str(path) for path in collection)
        return len(missing)

    @property
    def media_file_count(self) -> int:
        return max(self.organize_plan.media_file_count, self.rename_plan.media_file_count)

    @property
    def duplicate_group_count(self) -> int:
        return len(self.duplicate_scan.exact_groups)

    @property
    def duplicate_decision_count(self) -> int:
        return len(self.duplicate_bundle.decisions)


def build_cleanup_dry_run(options: CleanupWorkflowOptions) -> CleanupDryRun:
    duplicate_scan = scan_exact_duplicates(DuplicateScanConfig(source_dirs=list(options.source_dirs)))

    decisions: dict[str, str] = {}
    if options.duplicate_policy is not None:
        decisions = build_duplicate_decisions(duplicate_scan.exact_groups, options.duplicate_policy)

    duplicate_bundle = build_duplicate_workflow_bundle(
        duplicate_scan.exact_groups,
        decisions,
        options.duplicate_mode,
        target_root=options.target_root,
    )

    organize_plan = build_organize_dry_run(
        OrganizePlannerOptions(
            source_dirs=options.source_dirs,
            target_root=options.target_root,
            pattern=options.organize_pattern,
            recursive=options.recursive,
            include_hidden=options.include_hidden,
            operation_mode="copy",
            exiftool_path=options.exiftool_path,
        )
    )

    rename_plan = build_rename_dry_run(
        RenamePlannerOptions(
            source_dirs=options.source_dirs,
            template=options.rename_template,
            recursive=options.recursive,
            include_hidden=options.include_hidden,
            exiftool_path=options.exiftool_path,
        )
    )

    return CleanupDryRun(
        options=options,
        duplicate_scan=duplicate_scan,
        duplicate_bundle=duplicate_bundle,
        organize_plan=organize_plan,
        rename_plan=rename_plan,
    )
