from __future__ import annotations

import re
from collections import Counter
from datetime import datetime
from pathlib import Path

from media_manager.core.metadata import FileInspection, inspect_media_file

from .models import DateResolution, FilenameDateMatch
from .parse import describe_timezone_status, format_resolution_value, parse_datetime_value

# Realistic year guard: reject dates before photography existed or far in the future.
# 1800 = earliest practical photography (Niepce experiments ~1820s, first photo 1826/27).
# Current year + 1 allows files dated slightly ahead (camera clock drift, next-year metadata).
_REALISTIC_YEAR_MIN = 1800
_REALISTIC_YEAR_MAX = datetime.now().year + 1


def _year_is_realistic(value: datetime) -> bool:
    return _REALISTIC_YEAR_MIN <= value.year <= _REALISTIC_YEAR_MAX

FILENAME_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("whatsapp_datetime", re.compile(r"WhatsApp (?:Image|Video) (\d{4}-\d{2}-\d{2}) at (\d{2}\.\d{2}\.\d{2})", re.IGNORECASE)),
    ("pixel_datetime_ms", re.compile(r"PXL[_-]?(\d{8})[_-](\d{6})\d{3}", re.IGNORECASE)),
    ("compact_datetime", re.compile(r"(?<!\d)(\d{8}[ _-]\d{6})(?!\d)")),
    ("iso_datetime", re.compile(r"(?<!\d)(\d{4}-\d{2}-\d{2}[ _T]\d{2}[-:.]\d{2}[-:.]\d{2})(?!\d)")),
    ("named_camera_datetime", re.compile(r"(?:IMG|VID|PXL|MVIMG|Screenshot)[-_]?(\d{8})[-_](\d{6})", re.IGNORECASE)),
    ("date_only", re.compile(r"(?<!\d)(\d{4}-\d{2}-\d{2}|\d{8})(?!\d)")),
)


def _parse_filename_match(pattern_name: str, matched_text: str) -> datetime | None:
    candidates = [
        matched_text,
        matched_text.replace(".", ":"),
        matched_text.replace(" ", "_"),
        matched_text.replace("T", " "),
        matched_text.replace(".", "-"),
    ]
    for candidate in candidates:
        parsed = parse_datetime_value(candidate)
        if parsed is not None:
            return parsed
    return None


def find_filename_datetime(file_path: Path) -> FilenameDateMatch | None:
    name = file_path.stem
    for pattern_name, pattern in FILENAME_PATTERNS:
        match = pattern.search(name)
        if match is None:
            continue
        if pattern_name in {"named_camera_datetime", "pixel_datetime_ms"}:
            matched_text = f"{match.group(1)}_{match.group(2)}"
        elif pattern_name == "whatsapp_datetime":
            matched_text = f"{match.group(1)} {match.group(2)}"
        else:
            matched_text = match.group(1)
        parsed = _parse_filename_match(pattern_name, matched_text)
        if parsed is not None:
            return FilenameDateMatch(pattern_name=pattern_name, matched_text=matched_text, parsed_datetime=parsed)
    return None


def _candidate_counts(inspection: FileInspection) -> tuple[list[tuple[object, datetime]], int, int]:
    parseable_candidates: list[tuple[object, datetime]] = []
    unparseable_candidates = 0
    unrealistic_year_count = 0
    for candidate in inspection.date_candidates:
        parsed = parse_datetime_value(candidate.value)
        if parsed is None:
            unparseable_candidates += 1
            continue
        if not _year_is_realistic(parsed):
            unrealistic_year_count += 1
            continue
        parseable_candidates.append((candidate, parsed))
    return parseable_candidates, unparseable_candidates, unrealistic_year_count


def _build_metadata_reason(selected_source_tag: str, parseable_candidates: list[tuple[object, datetime]]) -> tuple[str, bool]:
    ignored_count = max(0, len(parseable_candidates) - 1)
    distinct_value_count = len({parsed for _, parsed in parseable_candidates})
    metadata_conflict = distinct_value_count > 1
    reason = f"Selected the highest-priority parseable metadata candidate from {selected_source_tag}."
    if ignored_count:
        label = "candidate" if ignored_count == 1 else "candidates"
        reason += f" ignored {ignored_count} lower-priority {label}."
    if len(parseable_candidates) > 1:
        if metadata_conflict:
            reason += f" parseable metadata candidates disagreed across {distinct_value_count} distinct values."
        else:
            reason += " remaining parseable metadata candidates agreed with the selected value."
    return reason, metadata_conflict


def resolve_capture_datetime(
    file_path: Path,
    *,
    inspection: FileInspection | None = None,
    exiftool_path: Path | None = None,
) -> DateResolution:
    inspection = inspection or inspect_media_file(file_path, exiftool_path=exiftool_path)
    parseable_candidates, unparseable_candidates, unrealistic_year_count = _candidate_counts(inspection)

    total_skipped = unparseable_candidates + unrealistic_year_count

    if parseable_candidates:
        selected_candidate, parsed = parseable_candidates[0]
        reason, metadata_conflict = _build_metadata_reason(selected_candidate.source_tag, parseable_candidates)
        if unrealistic_year_count:
            label = "candidate" if unrealistic_year_count == 1 else "candidates"
            reason += f" Rejected {unrealistic_year_count} metadata {label} with unrealistic year (before {_REALISTIC_YEAR_MIN} or after {_REALISTIC_YEAR_MAX})."
        return DateResolution(
            path=file_path,
            resolved_datetime=parsed,
            resolved_value=format_resolution_value(parsed),
            source_kind="metadata",
            source_label=selected_candidate.source_tag,
            confidence="high",
            timezone_status=describe_timezone_status(parsed),
            reason=reason,
            candidates_checked=len(inspection.date_candidates),
            parseable_candidate_count=len(parseable_candidates),
            unparseable_candidate_count=total_skipped,
            metadata_conflict=metadata_conflict,
            decision_policy="highest_priority_parseable_metadata",
        )

    filename_match = find_filename_datetime(file_path)
    if filename_match is not None:
        if not _year_is_realistic(filename_match.parsed_datetime):
            # Filename date has unrealistic year — skip it, fall through to mtime
            reason = f"Filename pattern matched ({filename_match.matched_text}) but produced unrealistic year {filename_match.parsed_datetime.year} (before {_REALISTIC_YEAR_MIN} or after {_REALISTIC_YEAR_MAX}). Fell back to file modification time."
            if inspection.date_candidates:
                count = len(inspection.date_candidates)
                label = "candidate" if count == 1 else "candidates"
                reason = f"skipping {count} unparseable metadata {label}. " + reason
            if unrealistic_year_count:
                label = "candidate" if unrealistic_year_count == 1 else "candidates"
                reason += f" Also rejected {unrealistic_year_count} metadata {label} with unrealistic year."
            modified_at = datetime.fromtimestamp(file_path.stat().st_mtime)
            return DateResolution(
                path=file_path,
                resolved_datetime=modified_at,
                resolved_value=format_resolution_value(modified_at),
                source_kind="file_system",
                source_label="mtime",
                confidence="low",
                timezone_status=describe_timezone_status(modified_at),
                reason=reason,
                candidates_checked=len(inspection.date_candidates),
                parseable_candidate_count=0,
                unparseable_candidate_count=total_skipped,
                metadata_conflict=False,
                decision_policy="mtime_fallback",
            )
        reason = f"Fell back to a recognized filename pattern: {filename_match.matched_text}."
        if inspection.date_candidates:
            count = len(inspection.date_candidates)
            label = "candidate" if count == 1 else "candidates"
            reason = f"skipping {count} unparseable metadata {label}. " + reason
        if unrealistic_year_count:
            label = "candidate" if unrealistic_year_count == 1 else "candidates"
            reason += f" Rejected {unrealistic_year_count} metadata {label} with unrealistic year (before {_REALISTIC_YEAR_MIN} or after {_REALISTIC_YEAR_MAX})."
        return DateResolution(
            path=file_path,
            resolved_datetime=filename_match.parsed_datetime,
            resolved_value=format_resolution_value(filename_match.parsed_datetime),
            source_kind="filename",
            source_label=filename_match.pattern_name,
            confidence="medium",
            timezone_status=describe_timezone_status(filename_match.parsed_datetime),
            reason=reason,
            candidates_checked=len(inspection.date_candidates),
            parseable_candidate_count=0,
            unparseable_candidate_count=total_skipped,
            metadata_conflict=False,
            decision_policy="filename_fallback",
        )

    modified_at = datetime.fromtimestamp(file_path.stat().st_mtime)
    reason = "No parseable metadata or filename datetime was found, so the file modification time was used."
    if inspection.date_candidates:
        count = len(inspection.date_candidates)
        label = "candidate" if count == 1 else "candidates"
        reason = f"skipping {count} unparseable metadata {label}. " + reason
    if unrealistic_year_count:
        label = "candidate" if unrealistic_year_count == 1 else "candidates"
        reason += f" Rejected {unrealistic_year_count} metadata {label} with unrealistic year."
    return DateResolution(
        path=file_path,
        resolved_datetime=modified_at,
        resolved_value=format_resolution_value(modified_at),
        source_kind="file_system",
        source_label="mtime",
        confidence="low",
        timezone_status=describe_timezone_status(modified_at),
        reason=reason,
        candidates_checked=len(inspection.date_candidates),
        parseable_candidate_count=0,
        unparseable_candidate_count=total_skipped,
        metadata_conflict=False,
        decision_policy="mtime_fallback",
    )
