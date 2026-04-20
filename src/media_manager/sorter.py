from __future__ import annotations

from pathlib import Path

from .media_formats import is_supported_media_path


def is_media_file(path: Path) -> bool:
    return path.is_file() and is_supported_media_path(path)


def iter_media_files(source_dirs: list[Path]) -> list[Path]:
    seen: set[Path] = set()
    collected: list[Path] = []

    for source_dir in source_dirs:
        for file_path in source_dir.rglob("*"):
            if not is_media_file(file_path):
                continue
            resolved = file_path.resolve()
            if resolved in seen:
                continue
            seen.add(resolved)
            collected.append(file_path)

    return sorted(collected, key=lambda path: str(path).lower())
