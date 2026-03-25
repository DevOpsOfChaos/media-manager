from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

from .constants import DATE_TAG_PRIORITY

COMMON_EXIFTOOL_PATHS = [
    Path(r"C:\Program Files\exiftool\exiftool.exe"),
    Path(r"C:\Program Files\exiftool\exiftool(-k).exe"),
]


def resolve_exiftool_path(explicit_path: Path | None = None) -> Path | None:
    if explicit_path and explicit_path.is_file():
        return explicit_path

    env_path = os.environ.get("EXIFTOOL_PATH")
    if env_path:
        candidate = Path(env_path)
        if candidate.is_file():
            return candidate

    which_result = shutil.which("exiftool")
    if which_result:
        return Path(which_result)

    for candidate in COMMON_EXIFTOOL_PATHS:
        if candidate.is_file():
            return candidate

    return None


def read_metadata_date(file_path: Path, exiftool_path: Path | None = None) -> str | None:
    resolved_exiftool = resolve_exiftool_path(exiftool_path)
    if resolved_exiftool is None:
        return None

    try:
        result = subprocess.run(
            [str(resolved_exiftool), "-json", str(file_path)],
            capture_output=True,
            text=True,
            check=True,
            encoding="utf-8",
            errors="replace",
        )
    except (subprocess.CalledProcessError, OSError):
        return None

    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError:
        return None

    if not payload:
        return None

    metadata = payload[0]
    for tag in DATE_TAG_PRIORITY:
        value = metadata.get(tag)
        if isinstance(value, str) and value.strip():
            return value.strip()

    return None
