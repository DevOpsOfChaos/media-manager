from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass(slots=True, frozen=True)
class FilenameDateMatch:
    pattern_name: str
    matched_text: str
    parsed_datetime: datetime


@dataclass(slots=True, frozen=True)
class DateResolution:
    path: Path
    resolved_datetime: datetime
    resolved_value: str
    source_kind: str
    source_label: str
    confidence: str
    timezone_status: str
    reason: str
    candidates_checked: int
