from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

from media_manager.core.date_resolver import DateResolution
from media_manager.core.scanner import ScanSummary, ScannedFile


@dataclass(slots=True, frozen=True)
class OrganizePlannerOptions:
    source_dirs: tuple[Path, ...]
    target_root: Path
    pattern: str
    recursive: bool = True
    include_hidden: bool = False
    follow_symlinks: bool = False
    operation_mode: str = "copy"
    exiftool_path: Path | None = None


@dataclass(slots=True)
class OrganizePlanEntry:
    scanned_file: ScannedFile
    resolution: DateResolution | None
    operation_mode: str
    status: str
    reason: str
    target_relative_dir: Path | None = None
    target_path: Path | None = None

    @property
    def source_path(self) -> Path:
        return self.scanned_file.path

    @property
    def source_root(self) -> Path:
        return self.scanned_file.source_root


@dataclass(slots=True)
class OrganizeDryRun:
    options: OrganizePlannerOptions
    scan_summary: ScanSummary
    entries: list[OrganizePlanEntry] = field(default_factory=list)

    @property
    def planned_count(self) -> int:
        return sum(1 for item in self.entries if item.status == "planned")

    @property
    def skipped_count(self) -> int:
        return sum(1 for item in self.entries if item.status == "skipped")

    @property
    def conflict_count(self) -> int:
        return sum(1 for item in self.entries if item.status == "conflict")

    @property
    def error_count(self) -> int:
        return sum(1 for item in self.entries if item.status == "error")

    @property
    def missing_source_count(self) -> int:
        return len(self.scan_summary.missing_sources)

    @property
    def media_file_count(self) -> int:
        return self.scan_summary.media_file_count

    @property
    def status_summary(self) -> dict[str, int]:
        return dict(Counter(item.status for item in self.entries))

    @property
    def reason_summary(self) -> dict[str, int]:
        return dict(Counter(item.reason for item in self.entries))

    @property
    def resolution_source_summary(self) -> dict[str, int]:
        return dict(Counter(item.resolution.source_kind for item in self.entries if item.resolution is not None))

    @property
    def confidence_summary(self) -> dict[str, int]:
        return dict(Counter(item.resolution.confidence for item in self.entries if item.resolution is not None))


@dataclass(slots=True)
class OrganizeExecutionEntry:
    plan_entry: OrganizePlanEntry
    outcome: str
    reason: str

    @property
    def source_path(self) -> Path:
        return self.plan_entry.source_path

    @property
    def target_path(self) -> Path | None:
        return self.plan_entry.target_path


@dataclass(slots=True)
class OrganizeExecutionResult:
    plan: OrganizeDryRun
    entries: list[OrganizeExecutionEntry] = field(default_factory=list)

    @property
    def processed_count(self) -> int:
        return len(self.entries)

    @property
    def copied_count(self) -> int:
        return sum(1 for item in self.entries if item.outcome == "copied")

    @property
    def moved_count(self) -> int:
        return sum(1 for item in self.entries if item.outcome == "moved")

    @property
    def executed_count(self) -> int:
        return self.copied_count + self.moved_count

    @property
    def skipped_count(self) -> int:
        return sum(1 for item in self.entries if item.outcome == "skipped")

    @property
    def conflict_count(self) -> int:
        return sum(1 for item in self.entries if item.outcome == "conflict")

    @property
    def error_count(self) -> int:
        return sum(1 for item in self.entries if item.outcome == "error")

    @property
    def outcome_summary(self) -> dict[str, int]:
        return dict(Counter(item.outcome for item in self.entries))

    @property
    def reason_summary(self) -> dict[str, int]:
        return dict(Counter(item.reason for item in self.entries))
