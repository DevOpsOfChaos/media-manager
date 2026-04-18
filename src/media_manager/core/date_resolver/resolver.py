from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path

from media_manager.core.metadata import FileInspection, inspect_media_file

from .models import DateResolution, FilenameDateMatch
from .parse import describe_timezone_status, format_resolution_value, parse_datetime_value

FILENAME_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "compact_datetime",
        re.compile(r"(?<!\d)(\d{8}[ _-]\d{6})(?!\d)"),
    ),
    (
        "iso_datetime",
        re.compile(r"(?<!\d)(\d{4}-\d{2}-\d{2}[ _T]\d{2}[-:.]\d{2}[-:.]\d{2})(?!\d)"),
    ),
    (
        "named_camera_datetime",
        re.compile(r"(?:IMG|VID|PXL|MVIMG|Screenshot)[-_]?(\d{8})[-_](\d{6})", re.IGNORECASE),
    ),
    (
        "date_only",
        re.compile(r"(?<!\d)(\d{4}-\d{2}-\d{2}|\d{8})(?!\d)"),
    ),
)


def _parse_filename_match(pattern_name: str, matched_text: str) -> datetime | None:
    normalized = matched_text.replace(".", ":")
    if pattern_name == "named_camera_datetime" and len(normalized) == 15 and "_" in normalized:
        normalized = normalized

    candidates = [
        normalized,
        normalized.replace(" ", "_"),
        normalized.replace("T", " "),
        normalized.replace(".", "-"),
    ]

    for candidate in candidates:
        parsed = parse_datetime_value(candidate)
        if parsed is not None:
            return parsed

    if re.fullmatch(r"\d{8}", normalized):
        return datetime.strptime(normalized, "%Y%m%d")
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", normalized):
        return datetime.strptime(normalized, "%Y-%m-%d")
    return None


def find_filename_datetime(file_path: Path) -> FilenameDateMatch | None:
    name = file_path.stem

    for pattern_name, pattern in FILENAME_PATTERNS:
        match = pattern.search(name)
        if match is None:
            continue

        if pattern_name == "named_camera_datetime":
            matched_text = f"{match.group(1)}_{match.group(2)}"
        else:
            matched_text = match.group(1)

        parsed = _parse_filename_match(pattern_name, matched_text)
        if parsed is not None:
            return FilenameDateMatch(
                pattern_name=pattern_name,
                matched_text=matched_text,
                parsed_datetime=parsed,
            )

    return None


def resolve_capture_datetime(
    file_path: Path,
    *,
    inspection: FileInspection | None = None,
    exiftool_path: Path | None = None,
) -> DateResolution:
    inspection = inspection or inspect_media_file(file_path, exiftool_path=exiftool_path)

    for candidate in inspection.date_candidates:
        parsed = parse_datetime_value(candidate.value)
        if parsed is None:
            continue
        return DateResolution(
            path=file_path,
            resolved_datetime=parsed,
            resolved_value=format_resolution_value(parsed),
            source_kind="metadata",
            source_label=candidate.source_tag,
            confidence="high",
            timezone_status=describe_timezone_status(parsed),
            reason=f"Selected the first parseable metadata candidate from {candidate.source_tag}.",
            candidates_checked=len(inspection.date_candidates),
        )

    filename_match = find_filename_datetime(file_path)
    if filename_match is not None:
        return DateResolution(
            path=file_path,
            resolved_datetime=filename_match.parsed_datetime,
            resolved_value=format_resolution_value(filename_match.parsed_datetime),
            source_kind="filename",
            source_label=filename_match.pattern_name,
            confidence="medium",
            timezone_status=describe_timezone_status(filename_match.parsed_datetime),
            reason=f"Fell back to a recognized filename pattern: {filename_match.matched_text}.",
            candidates_checked=len(inspection.date_candidates),
        )

    stat = file_path.stat()
    modified_at = datetime.fromtimestamp(stat.st_mtime)
    return DateResolution(
        path=file_path,
        resolved_datetime=modified_at,
        resolved_value=format_resolution_value(modified_at),
        source_kind="file_system",
        source_label="mtime",
        confidence="low",
        timezone_status=describe_timezone_status(modified_at),
        reason="No parseable metadata or filename datetime was found, so the file modification time was used.",
        candidates_checked=len(inspection.date_candidates),
    )
