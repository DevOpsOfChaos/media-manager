from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

from media_manager.core.date_resolver import DateResolution
from media_manager.core.scanner import ScanSummary, ScannedFile


@dataclass(slots=True, frozen=True)
class RenamePlannerOptions:
    source_dirs: tuple[Path, ...]
    template: str
    recursive: bool = True
    include_hidden: bool = False
    follow_symlinks: bool = False
    exiftool_path: Path | None = None


@dataclass(slots=True)
class RenamePlanEntry:
    scanned_file: ScannedFile
    resolution: DateResolution | None
    status: str
    reason: str
    rendered_name: str | None = None
    target_path: Path | None = None

    @property
    def source_path(self) -> Path:
        return self.scanned_file.path

    @property
    def source_root(self) -> Path:
        return self.scanned_file.source_root


@dataclass(slots=True)
class RenameDryRun:
    options: RenamePlannerOptions
    scan_summary: ScanSummary
    entries: list[RenamePlanEntry] = field(default_factory=list)

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
class RenameExecutionEntry:
    source_path: Path
    target_path: Path | None
    status: str
    reason: str
    action: str


@dataclass(slots=True)
class RenameExecutionResult:
    apply_requested: bool
    entries: list[RenameExecutionEntry] = field(default_factory=list)
    processed_count: int = 0
    preview_count: int = 0
    renamed_count: int = 0
    skipped_count: int = 0
    conflict_count: int = 0
    error_count: int = 0

    @property
    def status_summary(self) -> dict[str, int]:
        return dict(Counter(item.status for item in self.entries))

    @property
    def action_summary(self) -> dict[str, int]:
        return dict(Counter(item.action for item in self.entries))

    @property
    def reason_summary(self) -> dict[str, int]:
        return dict(Counter(item.reason for item in self.entries))
