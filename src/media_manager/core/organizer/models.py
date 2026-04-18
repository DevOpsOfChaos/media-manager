from __future__ import annotations

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
