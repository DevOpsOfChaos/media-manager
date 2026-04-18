from __future__ import annotations

import os
import re
import shutil
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path

from media_manager.core.date_resolver import DateResolution, resolve_capture_datetime
from media_manager.core.scanner import ScanOptions, ScanSummary, ScannedFile, scan_media_sources


_INVALID_SEGMENT_CHARS = '<>:"/\\|?*'


def _sanitize_segment(value: str) -> str:
    cleaned = value.strip()
    for char in _INVALID_SEGMENT_CHARS:
        cleaned = cleaned.replace(char, "_")
    cleaned = re.sub(r"\s+", " ", cleaned)
    cleaned = cleaned.strip(" .")
    return cleaned or "trip"


def parse_trip_date(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()


@dataclass(slots=True, frozen=True)
class TripWorkflowOptions:
    source_dirs: tuple[Path, ...]
    target_root: Path
    label: str
    start_date: date
    end_date: date
    recursive: bool = True
    include_hidden: bool = False
    follow_symlinks: bool = False
    mode: str = "link"
    exiftool_path: Path | None = None


@dataclass(slots=True)
class TripPlanEntry:
    scanned_file: ScannedFile
    resolution: DateResolution | None
    status: str
    reason: str
    mode: str
    collection_root: Path
    target_path: Path | None = None

    @property
    def source_path(self) -> Path:
        return self.scanned_file.path

    @property
    def source_root(self) -> Path:
        return self.scanned_file.source_root


@dataclass(slots=True)
class TripDryRun:
    options: TripWorkflowOptions
    scan_summary: ScanSummary
    entries: list[TripPlanEntry] = field(default_factory=list)

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
    def selected_count(self) -> int:
        return sum(1 for item in self.entries if item.status in {"planned", "skipped", "conflict"} and item.reason != "resolved capture date is outside the requested trip range")

    @property
    def missing_source_count(self) -> int:
        return len(self.scan_summary.missing_sources)

    @property
    def media_file_count(self) -> int:
        return self.scan_summary.media_file_count


@dataclass(slots=True)
class TripExecutionEntry:
    source_path: Path
    target_path: Path | None
    outcome: str
    reason: str


@dataclass(slots=True)
class TripExecutionResult:
    apply_requested: bool
    entries: list[TripExecutionEntry] = field(default_factory=list)
    processed_count: int = 0
    linked_count: int = 0
    copied_count: int = 0
    skipped_count: int = 0
    conflict_count: int = 0
    error_count: int = 0

    @property
    def executed_count(self) -> int:
        return self.linked_count + self.copied_count


def _normalized_key(path: Path) -> str:
    return os.path.normcase(str(path))


def _build_collection_root(options: TripWorkflowOptions) -> Path:
    year_segment = f"{options.start_date.year:04d}"
    label_segment = _sanitize_segment(options.label)
    return options.target_root / "Trips" / year_segment / label_segment


def _is_in_trip_range(resolution: DateResolution, options: TripWorkflowOptions) -> bool:
    resolved_date = resolution.resolved_datetime.date()
    return options.start_date <= resolved_date <= options.end_date


def build_trip_dry_run(options: TripWorkflowOptions) -> TripDryRun:
    if options.end_date < options.start_date:
        raise ValueError("Trip end date must be on or after the start date.")
    if options.mode not in {"link", "copy"}:
        raise ValueError("Trip workflow mode must be either 'link' or 'copy'.")

    scan_summary = scan_media_sources(
        ScanOptions(
            source_dirs=options.source_dirs,
            recursive=options.recursive,
            include_hidden=options.include_hidden,
            follow_symlinks=options.follow_symlinks,
        )
    )
    collection_root = _build_collection_root(options)
    dry_run = TripDryRun(options=options, scan_summary=scan_summary)
    seen_targets: dict[str, Path] = {}

    for scanned_file in scan_summary.files:
        try:
            resolution = resolve_capture_datetime(
                scanned_file.path,
                exiftool_path=options.exiftool_path,
            )
        except Exception as exc:
            dry_run.entries.append(
                TripPlanEntry(
                    scanned_file=scanned_file,
                    resolution=None,
                    status="error",
                    reason=str(exc),
                    mode=options.mode,
                    collection_root=collection_root,
                    target_path=None,
                )
            )
            continue

        if not _is_in_trip_range(resolution, options):
            dry_run.entries.append(
                TripPlanEntry(
                    scanned_file=scanned_file,
                    resolution=resolution,
                    status="skipped",
                    reason="resolved capture date is outside the requested trip range",
                    mode=options.mode,
                    collection_root=collection_root,
                    target_path=None,
                )
            )
            continue

        target_path = collection_root / _sanitize_segment(scanned_file.source_root.name) / scanned_file.relative_path
        target_key = _normalized_key(target_path)
        source_key = _normalized_key(scanned_file.path)

        if target_key == source_key:
            dry_run.entries.append(
                TripPlanEntry(
                    scanned_file=scanned_file,
                    resolution=resolution,
                    status="skipped",
                    reason="source file already matches the planned trip collection path",
                    mode=options.mode,
                    collection_root=collection_root,
                    target_path=target_path,
                )
            )
            continue

        if target_path.exists():
            try:
                if target_path.stat().st_size == scanned_file.size_bytes:
                    status = "skipped"
                    reason = "target already exists with matching file size"
                else:
                    status = "conflict"
                    reason = "target path already exists with a different file size"
            except OSError as exc:
                status = "error"
                reason = str(exc)

            dry_run.entries.append(
                TripPlanEntry(
                    scanned_file=scanned_file,
                    resolution=resolution,
                    status=status,
                    reason=reason,
                    mode=options.mode,
                    collection_root=collection_root,
                    target_path=target_path,
                )
            )
            continue

        if target_key in seen_targets:
            dry_run.entries.append(
                TripPlanEntry(
                    scanned_file=scanned_file,
                    resolution=resolution,
                    status="conflict",
                    reason="multiple source files would resolve to the same trip collection path",
                    mode=options.mode,
                    collection_root=collection_root,
                    target_path=target_path,
                )
            )
            continue

        seen_targets[target_key] = scanned_file.path
        dry_run.entries.append(
            TripPlanEntry(
                scanned_file=scanned_file,
                resolution=resolution,
                status="planned",
                reason="ready for trip workflow execution",
                mode=options.mode,
                collection_root=collection_root,
                target_path=target_path,
            )
        )

    dry_run.entries.sort(key=lambda item: _normalized_key(item.source_path))
    return dry_run


def execute_trip_plan(dry_run: TripDryRun, *, apply: bool) -> TripExecutionResult:
    result = TripExecutionResult(apply_requested=apply)

    for entry in dry_run.entries:
        result.processed_count += 1

        if entry.status == "skipped":
            result.skipped_count += 1
            result.entries.append(
                TripExecutionEntry(
                    source_path=entry.source_path,
                    target_path=entry.target_path,
                    outcome="skipped",
                    reason=entry.reason,
                )
            )
            continue

        if entry.status == "conflict":
            result.conflict_count += 1
            result.entries.append(
                TripExecutionEntry(
                    source_path=entry.source_path,
                    target_path=entry.target_path,
                    outcome="conflict",
                    reason=entry.reason,
                )
            )
            continue

        if entry.status == "error" or entry.target_path is None:
            result.error_count += 1
            result.entries.append(
                TripExecutionEntry(
                    source_path=entry.source_path,
                    target_path=entry.target_path,
                    outcome="error",
                    reason=entry.reason,
                )
            )
            continue

        if not apply:
            preview_outcome = "preview-link" if entry.mode == "link" else "preview-copy"
            result.entries.append(
                TripExecutionEntry(
                    source_path=entry.source_path,
                    target_path=entry.target_path,
                    outcome=preview_outcome,
                    reason=entry.reason,
                )
            )
            continue

        try:
            entry.target_path.parent.mkdir(parents=True, exist_ok=True)
            if entry.mode == "link":
                os.link(entry.source_path, entry.target_path)
                result.linked_count += 1
                outcome = "linked"
            else:
                shutil.copy2(entry.source_path, entry.target_path)
                result.copied_count += 1
                outcome = "copied"

            result.entries.append(
                TripExecutionEntry(
                    source_path=entry.source_path,
                    target_path=entry.target_path,
                    outcome=outcome,
                    reason="trip workflow action executed successfully",
                )
            )
        except Exception as exc:  # pragma: no cover - runtime safeguard
            result.error_count += 1
            result.entries.append(
                TripExecutionEntry(
                    source_path=entry.source_path,
                    target_path=entry.target_path,
                    outcome="error",
                    reason=str(exc),
                )
            )

    return result
