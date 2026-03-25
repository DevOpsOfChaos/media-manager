from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any

from media_manager.constants import DATE_TAG_PRIORITY
from media_manager.dates import parse_exif_date


class ExifToolError(RuntimeError):
    pass


def discover_exiftool(explicit_path: str | None = None) -> str:
    candidates: list[str] = []

    if explicit_path:
        candidates.append(explicit_path)

    env_path = os.environ.get("EXIFTOOL_PATH")
    if env_path:
        candidates.append(env_path)

    which_unix = shutil.which("exiftool")
    if which_unix:
        candidates.append(which_unix)

    which_windows = shutil.which("exiftool.exe")
    if which_windows:
        candidates.append(which_windows)

    candidates.extend([
        r"C:\Program Files\exiftool\exiftool.exe",
        r"C:\Program Files\exiftool\exiftool(-k).exe",
    ])

    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return candidate

    raise ExifToolError(
        "ExifTool wurde nicht gefunden. Installiere ExifTool oder setze EXIFTOOL_PATH."
    )


class ExifToolClient:
    def __init__(self, executable: str):
        self.executable = executable

    def get_version(self) -> str:
        try:
            result = subprocess.run(
                [self.executable, "-ver"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=True,
            )
        except Exception as exc:  # pragma: no cover
            raise ExifToolError(f"ExifTool konnte nicht gestartet werden: {exc}") from exc
        return result.stdout.strip()

    def read_metadata(self, file_path: Path) -> dict[str, Any]:
        try:
            result = subprocess.run(
                [self.executable, "-j", "-a", "-G0:1", "-s", str(file_path)],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=True,
            )
            payload = json.loads(result.stdout)
            if payload:
                return payload[0]
            return {}
        except Exception as exc:
            raise ExifToolError(f"Metadaten konnten nicht gelesen werden für {file_path}: {exc}") from exc


def pick_best_date(metadata: dict[str, Any]):
    for preferred_tag in DATE_TAG_PRIORITY:
        for key, value in metadata.items():
            if key.endswith(":" + preferred_tag):
                dt = parse_exif_date(str(value))
                if dt:
                    return dt, key, value
    return None, None, None
