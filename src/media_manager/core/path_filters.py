from __future__ import annotations

from fnmatch import fnmatchcase
from pathlib import Path
from typing import Iterable


def _normalize_pattern(pattern: str) -> str:
    return pattern.replace('\\', '/').casefold()


def _candidate_values(path: Path, *, source_root: Path | None = None) -> tuple[str, ...]:
    values = [path.name, path.as_posix(), str(path).replace('\\', '/')]
    if source_root is not None:
        try:
            relative = path.relative_to(source_root)
        except ValueError:
            relative = None
        if relative is not None:
            values.extend([relative.as_posix(), str(relative).replace('\\', '/')])
    normalized: list[str] = []
    seen: set[str] = set()
    for value in values:
        text = value.casefold()
        if text in seen:
            continue
        seen.add(text)
        normalized.append(text)
    return tuple(normalized)


def path_matches_any_pattern(path: Path, patterns: Iterable[str], *, source_root: Path | None = None) -> bool:
    pattern_list = tuple(str(item) for item in patterns if str(item))
    if not pattern_list:
        return False
    candidates = _candidate_values(path, source_root=source_root)
    for pattern in pattern_list:
        normalized_pattern = _normalize_pattern(pattern)
        for candidate in candidates:
            if fnmatchcase(candidate, normalized_pattern):
                return True
    return False


def path_is_included_by_patterns(
    path: Path,
    *,
    include_patterns: Iterable[str] = (),
    exclude_patterns: Iterable[str] = (),
    source_root: Path | None = None,
) -> bool:
    includes = tuple(str(item) for item in include_patterns if str(item))
    excludes = tuple(str(item) for item in exclude_patterns if str(item))
    if includes and not path_matches_any_pattern(path, includes, source_root=source_root):
        return False
    if excludes and path_matches_any_pattern(path, excludes, source_root=source_root):
        return False
    return True


__all__ = [
    "path_is_included_by_patterns",
    "path_matches_any_pattern",
]
