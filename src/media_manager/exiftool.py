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
COMMON_EXIFTOOL_NAMES = ("exiftool", "exiftool.exe", "exiftool(-k).exe")


def _resolve_explicit_candidate(candidate: Path) -> Path | None:
    expanded = candidate.expanduser()
    if expanded.is_file():
        return expanded
    if expanded.is_dir():
        for name in COMMON_EXIFTOOL_NAMES:
            nested = expanded / name
            if nested.is_file():
                return nested
    if expanded.suffix == "":
        for suffix_name in (expanded.name + ".exe", expanded.name + "(-k).exe"):
            nested = expanded.with_name(suffix_name)
            if nested.is_file():
                return nested
    return None


def resolve_exiftool_path(explicit_path: Path | None = None) -> Path | None:
    if explicit_path:
        resolved = _resolve_explicit_candidate(Path(explicit_path))
        if resolved is not None:
            return resolved

    env_path = os.environ.get("EXIFTOOL_PATH")
    if env_path:
        resolved = _resolve_explicit_candidate(Path(env_path))
        if resolved is not None:
            return resolved

    for name in ("exiftool", "exiftool.exe"):
        which_result = shutil.which(name)
        if which_result:
            return Path(which_result)

    for candidate in COMMON_EXIFTOOL_PATHS:
        if candidate.is_file():
            return candidate

    return None



def read_metadata_date(file_path: Path, exiftool_path: Path | None = None) -> str | None:
    metadata, _, _, _ = read_exiftool_metadata(
        file_path,
        exiftool_path=exiftool_path,
        include_time_tags=False,
        group_names=False,
    )
    if not metadata:
        return None

    for tag in DATE_TAG_PRIORITY:
        value = metadata.get(tag)
        if isinstance(value, str) and value.strip():
            return value.strip()

    return None



def read_exiftool_metadata(
    file_path: Path,
    exiftool_path: Path | None = None,
    *,
    include_time_tags: bool = True,
    group_names: bool = True,
    timeout_seconds: float = 20.0,
) -> tuple[dict[str, object] | None, bool, str | None, str | None]:
    resolved_exiftool = resolve_exiftool_path(exiftool_path)
    if resolved_exiftool is None:
        return None, False, "not_found", None

    command = [str(resolved_exiftool), "-json"]
    if include_time_tags:
        command.append("-time:all")
    if group_names:
        command.extend(["-G0:1", "-s"])
    command.append(str(file_path))

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout_seconds,
        )
    except subprocess.TimeoutExpired as exc:
        return None, True, "timeout", str(exc)
    except subprocess.CalledProcessError as exc:
        stderr = exc.stderr.strip() if isinstance(exc.stderr, str) else ""
        return None, True, "command_error", stderr or str(exc)
    except OSError as exc:
        return None, True, "command_error", str(exc)

    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        return None, True, "invalid_json", f"invalid_json: {exc}"

    if not payload or not isinstance(payload, list) or not isinstance(payload[0], dict):
        return {}, True, None, None
    return payload[0], True, None, None
