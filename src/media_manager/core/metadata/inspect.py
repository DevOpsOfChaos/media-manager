from __future__ import annotations

import json
import subprocess
from datetime import datetime
from pathlib import Path

from media_manager.constants import DATE_TAG_PRIORITY
from media_manager.exiftool import resolve_exiftool_path

from .models import DateCandidate, FileInspection

TIME_OUTPUT_FORMAT = "%Y-%m-%d %H:%M:%S"


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
    seen: set[tuple[str, str]] = set()

    for priority_index, tag in enumerate(DATE_TAG_PRIORITY):
        direct_value = normalized.get(tag)
        if direct_value:
            marker = (tag, direct_value)
            if marker not in seen:
                seen.add(marker)
                candidates.append(DateCandidate(source_tag=tag, value=direct_value, priority_index=priority_index))

        grouped_matches = sorted(
            (
                (key, value)
                for key, value in normalized.items()
                if key.endswith(f":{tag}")
            ),
            key=lambda item: item[0].lower(),
        )
        for key, value in grouped_matches:
            marker = (key, value)
            if marker in seen:
                continue
            seen.add(marker)
            candidates.append(DateCandidate(source_tag=key, value=value, priority_index=priority_index))

    return candidates



def _read_exiftool_metadata(file_path: Path, exiftool_path: Path | None = None) -> tuple[dict[str, object] | None, bool, str | None]:
    resolved_exiftool = resolve_exiftool_path(exiftool_path)
    if resolved_exiftool is None:
        return None, False, None

    try:
        result = subprocess.run(
            [str(resolved_exiftool), "-json", "-time:all", "-G0:1", "-s", str(file_path)],
            capture_output=True,
            text=True,
            check=True,
            encoding="utf-8",
            errors="replace",
        )
    except (subprocess.CalledProcessError, OSError) as exc:
        return None, True, str(exc)

    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        return None, True, f"invalid_json: {exc}"

    if not payload or not isinstance(payload, list) or not isinstance(payload[0], dict):
        return {}, True, None
    return payload[0], True, None



def inspect_media_file(file_path: Path, exiftool_path: Path | None = None) -> FileInspection:
    stat = file_path.stat()
    file_modified_value = datetime.fromtimestamp(stat.st_mtime).strftime(TIME_OUTPUT_FORMAT)

    metadata, exiftool_available, error = _read_exiftool_metadata(file_path, exiftool_path)
    candidates = extract_date_candidates(metadata or {}) if metadata is not None else []

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
        error=error,
    )
