from __future__ import annotations

from pathlib import Path

from .media_formats import is_supported_media_path, normalize_extensions


def is_media_file(path: Path, *, media_extensions: set[str] | frozenset[str] | None = None) -> bool:
    if not path.is_file():
        return False
    if media_extensions is not None:
        return path.suffix.lower() in media_extensions
    return is_supported_media_path(path)


def iter_media_files(source_dirs: list[Path], *, media_extensions: set[str] | frozenset[str] | None = None) -> list[Path]:
    seen: set[Path] = set()
    collected: list[Path] = []
    extension_filter = None if media_extensions is None else normalize_extensions(set(media_extensions))

    for source_dir in source_dirs:
        for file_path in source_dir.rglob("*"):
            if not is_media_file(file_path, media_extensions=extension_filter):
                continue
            resolved = file_path.resolve()
            if resolved in seen:
                continue
            seen.add(resolved)
            collected.append(file_path)

    return sorted(collected, key=lambda path: str(path).lower())
