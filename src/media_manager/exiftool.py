from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

from .constants import DATE_TAG_PRIORITY

COMMON_EXIFTOOL_PATHS: list[Path] = []
COMMON_EXIFTOOL_NAMES = ("exiftool", "exiftool.exe", "exiftool(-k).exe")

def _init_common_paths() -> list[Path]:
    """Build list of common exiftool locations across all drives and known install dirs."""
    candidates: list[Path] = []
    # Known install directories
    known_dirs = [
        Path("C:/Program Files/exiftool"),
        Path("C:/Program Files (x86)/exiftool"),
        Path.home() / "exiftool",
        Path.home() / "bin" / "exiftool",
        Path(os.environ.get("LOCALAPPDATA", "")) / "exiftool",
        Path(os.environ.get("APPDATA", "")) / "exiftool",
        Path("D:/Program Files/exiftool"),
        Path("D:/exiftool"),
    ]
    for d in known_dirs:
        try:
            d = d.expanduser().resolve()
        except Exception:
            continue
        for name in COMMON_EXIFTOOL_NAMES:
            p = d / name
            if p.is_file():
                candidates.append(p)
    return candidates

COMMON_EXIFTOOL_PATHS = _init_common_paths()


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


def _search_directory_for_exiftool(directory: Path, depth: int = 2) -> Path | None:
    """Search up to `depth` levels deep for any exiftool executable."""
    if depth < 0:
        return None
    try:
        for child in directory.iterdir():
            if child.is_file() and child.name.lower() in {n.lower() for n in COMMON_EXIFTOOL_NAMES}:
                return child
        if depth > 0:
            for child in directory.iterdir():
                if child.is_dir():
                    result = _search_directory_for_exiftool(child, depth - 1)
                    if result:
                        return result
    except (OSError, PermissionError):
        pass
    return None


def _find_in_program_files() -> Path | None:
    """Search Program Files directories for exiftool (one level deep)."""
    for base in [Path("C:/Program Files"), Path("C:/Program Files (x86)"), Path("D:/Program Files")]:
        if base.exists():
            result = _search_directory_for_exiftool(base, depth=1)
            if result:
                return result
    return None


def resolve_exiftool_path(explicit_path: Path | None = None) -> Path | None:
    # 1. Explicit path
    if explicit_path:
        resolved = _resolve_explicit_candidate(Path(explicit_path))
        if resolved is not None:
            return resolved

    # 2. Environment variable
    env_path = os.environ.get("EXIFTOOL_PATH")
    if env_path:
        resolved = _resolve_explicit_candidate(Path(env_path))
        if resolved is not None:
            return resolved

    # 3. PATH (fast)
    for name in ("exiftool", "exiftool.exe"):
        which_result = shutil.which(name)
        if which_result:
            return Path(which_result)

    # 4. Known common paths
    for candidate in COMMON_EXIFTOOL_PATHS:
        if candidate.is_file():
            return candidate

    # 5. Search Program Files (slower, cached)
    return _find_in_program_files()



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


def read_exiftool_metadata_batch(
    file_paths: list[Path],
    exiftool_path: Path | None = None,
    *,
    include_time_tags: bool = True,
    group_names: bool = True,
    timeout_seconds: float = 300.0,
) -> dict[Path, dict[str, object]]:
    """Read ExifTool metadata for multiple files in a single subprocess call.

    Returns a dict mapping each file path to its metadata dict.
    Files that fail to read are omitted from the result.
    """
    if not file_paths:
        return {}

    resolved_exiftool = resolve_exiftool_path(exiftool_path)
    if resolved_exiftool is None:
        return {}

    command = [str(resolved_exiftool), "-json"]
    if include_time_tags:
        command.append("-time:all")
    if group_names:
        command.extend(["-G0:1", "-s"])
    for fp in file_paths:
        command.append(str(fp))

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
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, OSError):
        return {}

    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError:
        return {}

    if not isinstance(payload, list):
        return {}

    metadata_map: dict[Path, dict[str, object]] = {}
    for item in payload:
        if not isinstance(item, dict):
            continue
        source_file = item.get("SourceFile", "")
        if source_file:
            metadata_map[Path(source_file)] = item
    return metadata_map
