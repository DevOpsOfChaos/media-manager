from __future__ import annotations

from datetime import datetime
from pathlib import Path

from media_manager.constants import DATE_TAG_PRIORITY
from media_manager.exiftool import read_exiftool_metadata, read_exiftool_metadata_batch

from .models import DateCandidate, FileInspection

TIME_OUTPUT_FORMAT = "%Y-%m-%d %H:%M:%S"


def _read_exiftool_metadata(file_path: Path, exiftool_path: Path | None = None):
    """Compatibility wrapper for legacy tests and monkeypatch hooks."""
    return read_exiftool_metadata(file_path, exiftool_path=exiftool_path)


def _normalize_metadata_keys(metadata: dict[str, object]) -> dict[str, str]:
    normalized: dict[str, str] = {}
    for key, value in metadata.items():
        if not isinstance(value, str):
            continue
        cleaned = value.strip()
        if not cleaned:
            continue
        normalized[str(key)] = cleaned
    return normalized


def extract_date_candidates(metadata: dict[str, object]) -> list[DateCandidate]:
    normalized = _normalize_metadata_keys(metadata)
    candidates: list[DateCandidate] = []
    seen_values: set[tuple[int, str]] = set()
    seen_sources: set[tuple[str, str]] = set()

    for priority_index, tag in enumerate(DATE_TAG_PRIORITY):
        direct_value = normalized.get(tag)
        if direct_value:
            marker = (tag, direct_value)
            if marker not in seen_sources:
                seen_sources.add(marker)
                value_marker = (priority_index, direct_value)
                if value_marker not in seen_values:
                    seen_values.add(value_marker)
                    candidates.append(DateCandidate(source_tag=tag, value=direct_value, priority_index=priority_index))

        grouped_matches = sorted(
            (item for item in normalized.items() if item[0].endswith(f":{tag}")),
            key=lambda item: item[0].lower(),
        )
        for key, value in grouped_matches:
            marker = (key, value)
            if marker in seen_sources:
                continue
            seen_sources.add(marker)
            value_marker = (priority_index, value)
            if value_marker in seen_values:
                continue
            seen_values.add(value_marker)
            candidates.append(DateCandidate(source_tag=key, value=value, priority_index=priority_index))

    return candidates


def inspect_media_file(file_path: Path, exiftool_path: Path | None = None) -> FileInspection:
    stat = file_path.stat()
    file_modified_value = datetime.fromtimestamp(stat.st_mtime).strftime(TIME_OUTPUT_FORMAT)

    metadata_result = _read_exiftool_metadata(file_path, exiftool_path=exiftool_path)
    if len(metadata_result) == 3:
        metadata, exiftool_available, error = metadata_result
        metadata_error_kind = None
    elif len(metadata_result) == 4:
        metadata, exiftool_available, metadata_error_kind, error = metadata_result
    else:
        raise ValueError("_read_exiftool_metadata must return a 3-tuple or 4-tuple")

    candidates = extract_date_candidates(metadata or {}) if metadata is not None else []
    metadata_tag_count = len(metadata or {}) if metadata is not None else 0

    if candidates:
        selected = candidates[0]
        return FileInspection(
            path=file_path,
            selected_value=selected.value,
            selected_source=selected.source_tag,
            date_candidates=candidates,
            file_modified_value=file_modified_value,
            metadata_available=True,
            exiftool_available=exiftool_available,
            metadata_tag_count=metadata_tag_count,
            metadata_error_kind=metadata_error_kind,
            error=error,
        )

    return FileInspection(
        path=file_path,
        selected_value=file_modified_value,
        selected_source="file_system:mtime",
        date_candidates=candidates,
        file_modified_value=file_modified_value,
        metadata_available=bool(metadata),
        exiftool_available=exiftool_available,
        metadata_tag_count=metadata_tag_count,
        metadata_error_kind=metadata_error_kind,
        error=error,
    )


def inspect_media_files_batch(
    file_paths: list[Path],
    exiftool_path: Path | None = None,
    *,
    timeout_seconds: float = 300.0,
) -> dict[Path, FileInspection]:
    """Inspect multiple media files with a single ExifTool subprocess call.

    Returns a dict mapping each file path to its FileInspection.
    Files that ExifTool cannot read fall back to file-system mtime.
    """
    if not file_paths:
        return {}

    metadata_map = read_exiftool_metadata_batch(
        file_paths, exiftool_path=exiftool_path, timeout_seconds=timeout_seconds,
    )

    inspections: dict[Path, FileInspection] = {}
    for file_path in file_paths:
        try:
            stat = file_path.stat()
        except OSError:
            continue
        file_modified_value = datetime.fromtimestamp(stat.st_mtime).strftime(TIME_OUTPUT_FORMAT)
        metadata = metadata_map.get(file_path)

        if metadata is not None:
            candidates = extract_date_candidates(metadata)
            metadata_tag_count = len(metadata)
            if candidates:
                selected = candidates[0]
                inspections[file_path] = FileInspection(
                    path=file_path,
                    selected_value=selected.value,
                    selected_source=selected.source_tag,
                    date_candidates=candidates,
                    file_modified_value=file_modified_value,
                    metadata_available=True,
                    exiftool_available=True,
                    metadata_tag_count=metadata_tag_count,
                )
                continue

        # Fallback: no metadata or no candidates — use file mtime
        inspections[file_path] = FileInspection(
            path=file_path,
            selected_value=file_modified_value,
            selected_source="file_system:mtime",
            date_candidates=[],
            file_modified_value=file_modified_value,
            metadata_available=metadata is not None,
            exiftool_available=bool(metadata_map),
            metadata_tag_count=len(metadata) if metadata else 0,
        )

    return inspections
