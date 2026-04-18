from __future__ import annotations

import os
from pathlib import Path

from media_manager.constants import MEDIA_EXTENSIONS

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


def scan_media_sources(options: ScanOptions) -> ScanSummary:
    media_extensions = options.media_extensions or frozenset(MEDIA_EXTENSIONS)
    source_dirs = _normalize_source_dirs(options.source_dirs)
    summary = ScanSummary(source_dirs=source_dirs)

    for source_root in source_dirs:
        if not source_root.exists() or not source_root.is_dir():
            summary.missing_sources.append(source_root)
            continue

        if options.recursive:
            candidate_iterator = []
            for current_root, dirnames, filenames in os.walk(source_root, followlinks=options.follow_symlinks):
                current_root_path = Path(current_root)
                if not options.include_hidden:
                    visible_dirnames: list[str] = []
                    for dirname in dirnames:
                        candidate_dir = current_root_path / dirname
                        if _is_hidden_path(candidate_dir, source_root):
                            summary.skipped_hidden_paths += 1
                            continue
                        visible_dirnames.append(dirname)
                    dirnames[:] = visible_dirnames
                for filename in sorted(filenames):
                    candidate_iterator.append(current_root_path / filename)
        else:
            candidate_iterator = list(_iter_top_level_files(source_root))

        for candidate in candidate_iterator:
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

            relative_path = candidate.relative_to(source_root)
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
