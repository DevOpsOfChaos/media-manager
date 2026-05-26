from __future__ import annotations

import os
from pathlib import Path
from typing import Generator

from media_manager.constants import MEDIA_EXTENSIONS
from media_manager.core.path_filters import path_is_included_by_patterns

from .models import ScanOptions, ScanSummary, ScannedFile


def _is_hidden_path(path: Path, source_root: Path) -> bool:
    try:
        relative_parts = path.relative_to(source_root).parts
    except ValueError:
        relative_parts = path.parts
    return any(part.startswith(".") for part in relative_parts if part not in {".", ".."})


def _normalize_source_dirs(source_dirs: tuple[Path, ...]) -> tuple[Path, ...]:
    seen: set[str] = set()
    normalized: list[Path] = []
    for item in source_dirs:
        resolved = Path(item).expanduser()
        key = str(resolved).lower()
        if key in seen:
            continue
        seen.add(key)
        normalized.append(resolved)
    return tuple(normalized)


def _iter_top_level_files(source_root: Path):
    for entry in sorted(source_root.iterdir(), key=lambda item: item.name.lower()):
        if entry.is_dir():
            continue
        yield entry


def _walk_depth(
    root: Path,
    max_depth: int | None,
    follow_symlinks: bool,
    include_hidden: bool,
    summary: ScanSummary,
):
    """Walk directory tree using os.scandir for cached stat information.

    Yields (file_path, file_size) tuples for files matching *extensions*.
    Hidden directories are pruned and counted in *summary* when *include_hidden* is False.
    """
    stack: list[tuple[Path, int]] = [(root, 0)]
    while stack:
        current, depth = stack.pop()
        if max_depth is not None and depth > max_depth:
            continue
        try:
            for entry in os.scandir(current):
                name = entry.name
                if entry.is_dir(follow_symlinks=False):
                    if not include_hidden and name.startswith("."):
                        summary.skipped_hidden_paths += 1
                        continue
                    stack.append((Path(entry.path), depth + 1))
                elif entry.is_dir(follow_symlinks=True):
                    if follow_symlinks:
                        if not include_hidden and name.startswith("."):
                            summary.skipped_hidden_paths += 1
                            continue
                        stack.append((Path(entry.path), depth + 1))
                else:
                    try:
                        size_bytes = entry.stat().st_size
                    except OSError:
                        size_bytes = 0
                    yield Path(entry.path), size_bytes
        except PermissionError:
            continue


def scan_media_sources(options: ScanOptions, use_cache: bool = False, max_depth: int | None = None) -> ScanSummary:
    # When use_cache=True, callers may skip rescan if source directory mtimes haven't changed.
    # A simple file-based cache (JSON mapping source_root -> last_mtime) can be checked before
    # invoking this function. This kwarg exists to document and enable that pattern.
    media_extensions = options.media_extensions or frozenset(MEDIA_EXTENSIONS)
    source_dirs = _normalize_source_dirs(options.source_dirs)
    summary = ScanSummary(source_dirs=source_dirs)

    for source_root in source_dirs:
        if not source_root.exists() or not source_root.is_dir():
            summary.missing_sources.append(source_root)
            continue

        if options.recursive:
            candidates = _walk_depth(
                source_root,
                max_depth=max_depth,
                follow_symlinks=options.follow_symlinks,
                include_hidden=options.include_hidden,
                summary=summary,
            )
        else:
            candidates = ((entry, None) for entry in _iter_top_level_files(source_root))

        for candidate, size_bytes in candidates:
            if not options.include_hidden and _is_hidden_path(candidate, source_root):
                summary.skipped_hidden_paths += 1
                continue
            if candidate.is_symlink() and not options.follow_symlinks:
                summary.skipped_non_media_files += 1
                continue
            if not candidate.is_file():
                continue

            extension = candidate.suffix.lower()
            if extension not in media_extensions:
                summary.skipped_non_media_files += 1
                continue

            if not path_is_included_by_patterns(
                candidate,
                include_patterns=options.include_patterns,
                exclude_patterns=options.exclude_patterns,
                source_root=source_root,
            ):
                summary.skipped_filtered_files += 1
                continue

            relative_path = candidate.relative_to(source_root)
            if size_bytes is None:
                try:
                    size_bytes = candidate.stat().st_size
                except OSError:
                    size_bytes = 0

            summary.files.append(
                ScannedFile(
                    source_root=source_root,
                    path=candidate,
                    relative_path=relative_path,
                    extension=extension,
                    size_bytes=size_bytes,
                )
            )

    summary.files.sort(key=lambda item: (str(item.source_root).lower(), str(item.relative_path).lower()))
    return summary


def scan_media_sources_streaming(
    source_dirs: tuple[Path, ...],
    extensions: frozenset[str] | None = None,
    *,
    max_depth: int = 3,
    max_files: int = 0,
) -> Generator[ScannedFile, None, None]:
    """Generator version of scan_media_sources — yields files one at a time.

    Uses less memory for very large libraries (160k+ files).
    No ScanSummary is built; callers get individual ScannedFile objects.

    Args:
        source_dirs: Directories to scan.
        extensions: File extensions to include (default: MEDIA_EXTENSIONS).
        max_depth: Maximum directory depth (0 = files in root only).
        max_files: Stop after this many files (0 = no limit).

    Yields:
        ScannedFile objects one at a time.
    """
    if extensions is None:
        extensions = MEDIA_EXTENSIONS

    count = 0
    normed = _normalize_source_dirs(source_dirs)

    for source_root in normed:
        stack: list[tuple[Path, int]] = [(source_root, 0)]
        while stack:
            current, depth = stack.pop()
            if depth > max_depth:
                continue

            try:
                with os.scandir(current) as entries:
                    for entry in entries:
                        if entry.is_dir(follow_symlinks=False):
                            if not entry.name.startswith("."):
                                stack.append((Path(entry.path), depth + 1))
                        elif entry.is_file(follow_symlinks=False):
                            ext = Path(entry.name).suffix.lower()
                            if ext in extensions:
                                try:
                                    st = entry.stat()
                                    relative = Path(entry.path).relative_to(source_root)
                                    yield ScannedFile(
                                        source_root=source_root,
                                        path=Path(entry.path),
                                        relative_path=relative,
                                        extension=ext,
                                        size_bytes=st.st_size,
                                    )
                                    count += 1
                                    if max_files and count >= max_files:
                                        return
                                except OSError:
                                    continue
            except PermissionError:
                continue
