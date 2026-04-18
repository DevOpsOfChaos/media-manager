from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True, frozen=True)
class DateCandidate:
    source_tag: str
    value: str
    priority_index: int


@dataclass(slots=True)
class FileInspection:
    path: Path
    selected_value: str
    selected_source: str
    date_candidates: list[DateCandidate] = field(default_factory=list)
    file_modified_value: str = ""
    metadata_available: bool = False
    exiftool_available: bool = False
    metadata_tag_count: int = 0
    metadata_error_kind: str | None = None
    error: str | None = None
