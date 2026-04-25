from __future__ import annotations

from dataclasses import dataclass, field
import os
from pathlib import Path
from typing import Literal

from media_manager.core.path_filters import path_is_included_by_patterns, path_matches_any_pattern

DoctorCommand = Literal["general", "organize", "rename", "cleanup", "duplicates", "inspect", "trip"]
DiagnosticSeverity = Literal["info", "warning", "error"]


@dataclass(slots=True, frozen=True)
class DoctorOptions:
    command: DoctorCommand = "general"
    source_dirs: tuple[Path, ...] = ()
    target_root: Path | None = None
    include_patterns: tuple[str, ...] = ()
    exclude_patterns: tuple[str, ...] = ()
    report_json_path: Path | None = None
    review_json_path: Path | None = None
    run_log_path: Path | None = None
    journal_path: Path | None = None
    history_dir: Path | None = None
    exiftool_path: Path | None = None
    recursive: bool = True
    include_hidden: bool = False
    follow_symlinks: bool = False
    max_scan_files: int = 5000


@dataclass(slots=True, frozen=True)
class DiagnosticEntry:
    code: str
    severity: DiagnosticSeverity
    message: str
    path: Path | None = None
    hint: str | None = None


@dataclass(slots=True)
class SourcePreview:
    source_root: Path
    exists: bool
    is_dir: bool
    scanned_file_count: int = 0
    included_file_count: int = 0
    excluded_by_include_count: int = 0
    excluded_by_exclude_count: int = 0
    hidden_skipped_count: int = 0
    scan_limited: bool = False


@dataclass(slots=True)
class DoctorReport:
    options: DoctorOptions
    diagnostics: list[DiagnosticEntry] = field(default_factory=list)
    source_previews: list[SourcePreview] = field(default_factory=list)

    @property
    def error_count(self) -> int:
        return sum(1 for item in self.diagnostics if item.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for item in self.diagnostics if item.severity == "warning")

    @property
    def info_count(self) -> int:
        return sum(1 for item in self.diagnostics if item.severity == "info")

    @property
    def ready(self) -> bool:
        return self.error_count == 0

    @property
    def status(self) -> str:
        if self.error_count > 0:
            return "blocked"
        if self.warning_count > 0:
            return "review_recommended"
        return "ready"

    @property
    def next_action(self) -> str:
        if self.error_count > 0:
            return "fix errors before running the workflow"
        if self.warning_count > 0:
            return "review warnings before running with --apply"
        return "workflow inputs look ready"


def _normalized_key(path: Path) -> str:
    return os.path.normcase(str(path))


def _normalize_patterns(patterns: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(str(item).strip() for item in patterns if str(item).strip())


def _is_hidden_path(path: Path, source_root: Path) -> bool:
    try:
        relative_parts = path.relative_to(source_root).parts
    except ValueError:
        relative_parts = path.parts
    return any(part.startswith(".") for part in relative_parts if part not in {".", ".."})


def _diagnostic(
    report: DoctorReport,
    code: str,
    severity: DiagnosticSeverity,
    message: str,
    *,
    path: Path | None = None,
    hint: str | None = None,
) -> None:
    report.diagnostics.append(DiagnosticEntry(code=code, severity=severity, message=message, path=path, hint=hint))


def _iter_candidate_files(source_root: Path, *, recursive: bool, follow_symlinks: bool):
    if recursive:
        for current_root, dirnames, filenames in os.walk(source_root, followlinks=follow_symlinks):
            current_root_path = Path(current_root)
            dirnames[:] = sorted(dirnames, key=str.lower)
            for filename in sorted(filenames, key=str.lower):
                yield current_root_path / filename
    else:
        for item in sorted(source_root.iterdir(), key=lambda entry: entry.name.lower()):
            if item.is_file():
                yield item


def _check_sources(report: DoctorReport) -> None:
    options = report.options
    seen: set[str] = set()
    if not options.source_dirs:
        _diagnostic(
            report,
            "source.none_provided",
            "warning",
            "No source directory was provided for diagnostics.",
            hint="Pass one or more --source values to preview workflow inputs.",
        )
        return

    for source in options.source_dirs:
        source_root = Path(source).expanduser()
        key = _normalized_key(source_root)
        if key in seen:
            _diagnostic(
                report,
                "source.duplicate",
                "warning",
                "The same source directory was provided more than once.",
                path=source_root,
                hint="Remove duplicate --source values to make summaries easier to read.",
            )
            continue
        seen.add(key)

        exists = source_root.exists()
        is_dir = source_root.is_dir() if exists else False
        preview = SourcePreview(source_root=source_root, exists=exists, is_dir=is_dir)
        report.source_previews.append(preview)

        if not exists:
            _diagnostic(report, "source.missing", "error", "Source directory does not exist.", path=source_root)
            continue
        if not is_dir:
            _diagnostic(report, "source.not_directory", "error", "Source path is not a directory.", path=source_root)
            continue
        if not os.access(source_root, os.R_OK):
            _diagnostic(report, "source.not_readable", "warning", "Source directory may not be readable.", path=source_root)

        scanned = 0
        for candidate in _iter_candidate_files(source_root, recursive=options.recursive, follow_symlinks=options.follow_symlinks):
            if scanned >= max(0, options.max_scan_files):
                preview.scan_limited = True
                break
            scanned += 1
            if not options.include_hidden and _is_hidden_path(candidate, source_root):
                preview.hidden_skipped_count += 1
                continue
            if candidate.is_symlink() and not options.follow_symlinks:
                continue
            if not candidate.is_file():
                continue
            preview.scanned_file_count += 1
            include_ok = True
            if options.include_patterns and not path_matches_any_pattern(
                candidate,
                options.include_patterns,
                source_root=source_root,
            ):
                include_ok = False
                preview.excluded_by_include_count += 1
            exclude_hit = path_matches_any_pattern(candidate, options.exclude_patterns, source_root=source_root)
            if exclude_hit:
                preview.excluded_by_exclude_count += 1
            if include_ok and not exclude_hit and path_is_included_by_patterns(
                candidate,
                include_patterns=options.include_patterns,
                exclude_patterns=options.exclude_patterns,
                source_root=source_root,
            ):
                preview.included_file_count += 1

        if preview.scan_limited:
            _diagnostic(
                report,
                "source.scan_limited",
                "info",
                "Source preview stopped at the configured scan limit.",
                path=source_root,
                hint="Increase --max-scan-files for a fuller diagnostic preview.",
            )
        if (options.include_patterns or options.exclude_patterns) and preview.scanned_file_count > 0 and preview.included_file_count == 0:
            _diagnostic(
                report,
                "filters.no_matches",
                "warning",
                "Include/exclude patterns leave this source with no included files in the diagnostic preview.",
                path=source_root,
                hint="Check quoting and path separators in --include-pattern / --exclude-pattern.",
            )


def _check_target(report: DoctorReport) -> None:
    options = report.options
    command_requires_target = options.command in {"organize", "cleanup"}
    if options.target_root is None:
        if command_requires_target:
            _diagnostic(
                report,
                "target.missing",
                "warning",
                f"The {options.command} workflow usually needs a target directory.",
                hint="Pass --target to verify target path readiness.",
            )
        return

    target = Path(options.target_root).expanduser()
    if target.exists() and target.is_file():
        _diagnostic(report, "target.is_file", "error", "Target path exists as a file.", path=target)
        return
    if target.exists() and target.is_dir():
        if not os.access(target, os.W_OK):
            _diagnostic(report, "target.not_writable", "warning", "Target directory may not be writable.", path=target)
        else:
            _diagnostic(report, "target.ready", "info", "Target directory exists.", path=target)
        return

    parent = target.parent
    if parent.exists() and parent.is_dir():
        if not os.access(parent, os.W_OK):
            _diagnostic(report, "target.parent_not_writable", "warning", "Target parent may not be writable.", path=parent)
        else:
            _diagnostic(
                report,
                "target.will_create",
                "info",
                "Target directory does not exist, but its parent exists.",
                path=target,
                hint="The workflow can create target directories during execution.",
            )
    else:
        _diagnostic(
            report,
            "target.parent_missing",
            "warning",
            "Target directory parent does not exist.",
            path=target,
            hint="Create the parent directory or choose an existing parent path.",
        )


def _check_output_paths(report: DoctorReport) -> None:
    output_paths = [
        ("report_json", report.options.report_json_path),
        ("review_json", report.options.review_json_path),
        ("run_log", report.options.run_log_path),
        ("journal", report.options.journal_path),
    ]
    for label, path in output_paths:
        if path is None:
            continue
        output_path = Path(path).expanduser()
        if output_path.exists() and output_path.is_dir():
            _diagnostic(
                report,
                f"output.{label}.is_directory",
                "error",
                "Output path points to a directory, not a file.",
                path=output_path,
            )
            continue
        parent = output_path.parent
        if parent.exists() and parent.is_file():
            _diagnostic(
                report,
                f"output.{label}.parent_is_file",
                "error",
                "Output parent path exists as a file.",
                path=parent,
            )
        elif not parent.exists():
            _diagnostic(
                report,
                f"output.{label}.parent_will_create",
                "info",
                "Output parent directory does not exist and would be created by export helpers.",
                path=parent,
            )

    if report.options.history_dir is not None:
        history_dir = Path(report.options.history_dir).expanduser()
        if history_dir.exists() and history_dir.is_file():
            _diagnostic(report, "history_dir.is_file", "error", "History path exists as a file.", path=history_dir)
        elif not history_dir.exists():
            _diagnostic(report, "history_dir.will_create", "info", "History directory does not exist yet.", path=history_dir)


def _check_patterns(report: DoctorReport) -> None:
    raw_patterns = list(report.options.include_patterns) + list(report.options.exclude_patterns)
    for pattern in raw_patterns:
        if not str(pattern).strip():
            _diagnostic(report, "filters.empty_pattern", "warning", "An empty include/exclude pattern was ignored.")
        elif any(part == ".." for part in str(pattern).replace("\\", "/").split("/")):
            _diagnostic(
                report,
                "filters.parent_navigation",
                "warning",
                "A pattern contains '..', which can be confusing for relative media filters.",
                hint="Prefer path-relative glob patterns such as 2024/* or *.jpg.",
            )


def _check_exiftool(report: DoctorReport) -> None:
    exiftool_path = report.options.exiftool_path
    if exiftool_path is None:
        return
    path = Path(exiftool_path).expanduser()
    if not path.exists():
        _diagnostic(report, "exiftool.missing", "warning", "Configured exiftool path does not exist.", path=path)
    elif path.is_dir():
        _diagnostic(report, "exiftool.is_directory", "warning", "Configured exiftool path is a directory.", path=path)


def build_doctor_report(options: DoctorOptions) -> DoctorReport:
    normalized_options = DoctorOptions(
        command=options.command,
        source_dirs=tuple(Path(item).expanduser() for item in options.source_dirs),
        target_root=None if options.target_root is None else Path(options.target_root).expanduser(),
        include_patterns=_normalize_patterns(options.include_patterns),
        exclude_patterns=_normalize_patterns(options.exclude_patterns),
        report_json_path=options.report_json_path,
        review_json_path=options.review_json_path,
        run_log_path=options.run_log_path,
        journal_path=options.journal_path,
        history_dir=options.history_dir,
        exiftool_path=options.exiftool_path,
        recursive=options.recursive,
        include_hidden=options.include_hidden,
        follow_symlinks=options.follow_symlinks,
        max_scan_files=max(0, int(options.max_scan_files)),
    )
    report = DoctorReport(options=normalized_options)
    _check_patterns(report)
    _check_sources(report)
    _check_target(report)
    _check_output_paths(report)
    _check_exiftool(report)
    return report


def build_doctor_payload(report: DoctorReport) -> dict[str, object]:
    return {
        "command": report.options.command,
        "status": report.status,
        "ready": report.ready,
        "next_action": report.next_action,
        "recursive": report.options.recursive,
        "include_hidden": report.options.include_hidden,
        "follow_symlinks": report.options.follow_symlinks,
        "max_scan_files": report.options.max_scan_files,
        "sources": [str(path) for path in report.options.source_dirs],
        "target_root": None if report.options.target_root is None else str(report.options.target_root),
        "include_patterns": list(report.options.include_patterns),
        "exclude_patterns": list(report.options.exclude_patterns),
        "summary": {
            "error_count": report.error_count,
            "warning_count": report.warning_count,
            "info_count": report.info_count,
            "source_count": len(report.source_previews),
            "included_file_count": sum(item.included_file_count for item in report.source_previews),
            "scanned_file_count": sum(item.scanned_file_count for item in report.source_previews),
        },
        "diagnostics": [
            {
                "code": item.code,
                "severity": item.severity,
                "message": item.message,
                "path": None if item.path is None else str(item.path),
                "hint": item.hint,
            }
            for item in report.diagnostics
        ],
        "source_previews": [
            {
                "source_root": str(item.source_root),
                "exists": item.exists,
                "is_dir": item.is_dir,
                "scanned_file_count": item.scanned_file_count,
                "included_file_count": item.included_file_count,
                "excluded_by_include_count": item.excluded_by_include_count,
                "excluded_by_exclude_count": item.excluded_by_exclude_count,
                "hidden_skipped_count": item.hidden_skipped_count,
                "scan_limited": item.scan_limited,
            }
            for item in report.source_previews
        ],
    }


__all__ = [
    "DiagnosticEntry",
    "DiagnosticSeverity",
    "DoctorCommand",
    "DoctorOptions",
    "DoctorReport",
    "SourcePreview",
    "build_doctor_payload",
    "build_doctor_report",
]
