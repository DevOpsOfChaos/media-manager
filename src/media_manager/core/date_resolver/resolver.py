from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path

from media_manager.core.metadata import FileInspection, inspect_media_file

from .models import DateResolution, FilenameDateMatch
from .parse import describe_timezone_status, format_resolution_value, parse_datetime_value

FILENAME_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "pixel_datetime_ms",
        re.compile(r"(?<!\d)(\d{8})[_-](\d{6})(\d{3})(?!\d)"),
    ),
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
        "whatsapp_datetime",
        re.compile(r"(\d{4}-\d{2}-\d{2})[ _-]at[ _-](\d{2}\.\d{2}\.\d{2})", re.IGNORECASE),
    ),
    (
        "date_only",
        re.compile(r"(?<!\d)(\d{4}-\d{2}-\d{2}|\d{8})(?!\d)"),
    ),
)


def _parse_filename_match(pattern_name: str, matched_text: str) -> datetime | None:
    normalized = matched_text.replace(".", ":")

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
        elif pattern_name == "whatsapp_datetime":
            matched_text = f"{match.group(1)} {match.group(2)}"
        elif pattern_name == "pixel_datetime_ms":
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



def _collect_parseable_metadata_candidates(inspection: FileInspection) -> list[tuple[object, datetime]]:
    parseable: list[tuple[object, datetime]] = []
    for candidate in inspection.date_candidates:
        parsed = parse_datetime_value(candidate.value)
        if parsed is None:
            continue
        parseable.append((candidate, parsed))
    return parseable



def _build_metadata_reason(chosen_candidate, chosen_datetime: datetime, parseable_candidates: list[tuple[object, datetime]]) -> str:
    parseable_count = len(parseable_candidates)
    if parseable_count == 1:
        return f"Selected the highest-priority parseable metadata candidate from {chosen_candidate.source_tag}."

    differing_lower_candidates = [
        candidate
        for candidate, parsed in parseable_candidates[1:]
        if format_resolution_value(parsed) != format_resolution_value(chosen_datetime)
    ]
    if differing_lower_candidates:
        return (
            f"Selected the highest-priority parseable metadata candidate from {chosen_candidate.source_tag} "
            f"and ignored {len(differing_lower_candidates)} lower-priority candidate(s) with different values."
        )
    return (
        f"Selected the highest-priority parseable metadata candidate from {chosen_candidate.source_tag}. "
        f"{parseable_count} parseable metadata candidate(s) agreed on the same value."
    )



def resolve_capture_datetime(
    file_path: Path,
    *,
    inspection: FileInspection | None = None,
    exiftool_path: Path | None = None,
) -> DateResolution:
    inspection = inspection or inspect_media_file(file_path, exiftool_path=exiftool_path)

    parseable_metadata_candidates = _collect_parseable_metadata_candidates(inspection)
    if parseable_metadata_candidates:
        chosen_candidate, chosen_datetime = parseable_metadata_candidates[0]
        return DateResolution(
            path=file_path,
            resolved_datetime=chosen_datetime,
            resolved_value=format_resolution_value(chosen_datetime),
            source_kind="metadata",
            source_label=chosen_candidate.source_tag,
            confidence="high",
            timezone_status=describe_timezone_status(chosen_datetime),
            reason=_build_metadata_reason(chosen_candidate, chosen_datetime, parseable_metadata_candidates),
            candidates_checked=len(inspection.date_candidates),
        )

    filename_match = find_filename_datetime(file_path)
    if filename_match is not None:
        metadata_context = ""
        if inspection.date_candidates:
            metadata_context = f" after skipping {len(inspection.date_candidates)} unparseable metadata candidate(s)"
        return DateResolution(
            path=file_path,
            resolved_datetime=filename_match.parsed_datetime,
            resolved_value=format_resolution_value(filename_match.parsed_datetime),
            source_kind="filename",
            source_label=filename_match.pattern_name,
            confidence="medium",
            timezone_status=describe_timezone_status(filename_match.parsed_datetime),
            reason=(
                f"Fell back to a recognized filename pattern ({filename_match.pattern_name}: {filename_match.matched_text})"
                f"{metadata_context}."
            ),
            candidates_checked=len(inspection.date_candidates),
        )

    stat = file_path.stat()
    modified_at = datetime.fromtimestamp(stat.st_mtime)
    metadata_context = ""
    if inspection.date_candidates:
        metadata_context = f" after skipping {len(inspection.date_candidates)} unparseable metadata candidate(s)"
    return DateResolution(
        path=file_path,
        resolved_datetime=modified_at,
        resolved_value=format_resolution_value(modified_at),
        source_kind="file_system",
        source_label="mtime",
        confidence="low",
        timezone_status=describe_timezone_status(modified_at),
        reason=(
            "No parseable metadata or filename datetime was found"
            f"{metadata_context}, so the file modification time was used."
        ),
        candidates_checked=len(inspection.date_candidates),
    )
