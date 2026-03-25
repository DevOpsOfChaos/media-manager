from __future__ import annotations

from pathlib import Path


def _normalized_key(path: Path) -> tuple[str, str]:
    return (str(path).lower(), str(path))


def default_keep_path(paths: list[Path]) -> Path:
    if not paths:
        raise ValueError("paths must not be empty")
    return sorted(paths, key=_normalized_key)[0]


def newest_keep_path(paths: list[Path]) -> Path:
    if not paths:
        raise ValueError("paths must not be empty")
    return max(paths, key=lambda path: (path.stat().st_mtime_ns, str(path).lower()))


def oldest_keep_path(paths: list[Path]) -> Path:
    if not paths:
        raise ValueError("paths must not be empty")
    return min(paths, key=lambda path: (path.stat().st_mtime_ns, str(path).lower()))


def paths_marked_for_removal(paths: list[Path], keep_path: Path) -> list[Path]:
    return [path for path in paths if path != keep_path]


def count_marked_for_removal(paths: list[Path], keep_path: Path) -> int:
    return len(paths_marked_for_removal(paths, keep_path))
