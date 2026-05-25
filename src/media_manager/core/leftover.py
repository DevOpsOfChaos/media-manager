from __future__ import annotations

import os
import shutil
from dataclasses import dataclass, field
from pathlib import Path


def _normalized_path_key(path: Path) -> str:
    return os.path.normcase(str(path))


@dataclass(slots=True, frozen=True)
class LeftoverConsolidationEntry:
    source_root: Path
    source_path: Path
    target_path: Path
    conflict_resolved: bool = False


@dataclass(slots=True)
class LeftoverConsolidationResult:
    directory_name: str
    entries: list[LeftoverConsolidationEntry] = field(default_factory=list)
    removed_empty_directories: list[Path] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def file_count(self) -> int:
        return len(self.entries)

    @property
    def removed_empty_directory_count(self) -> int:
        return len(self.removed_empty_directories)

    @property
    def conflict_count(self) -> int:
        return sum(1 for item in self.entries if item.conflict_resolved)

    @property
    def error_count(self) -> int:
        return len(self.errors)


def discover_leftover_files(source_root: Path, leftover_dir_name: str) -> list[Path]:
    """Discover all files in source_root that are NOT inside the leftover directory."""
    leftover_dir = source_root / leftover_dir_name
    files: list[Path] = []
    if not source_root.exists():
        return files
    for current_root, dirnames, filenames in os.walk(source_root, topdown=True):
        current_root_path = Path(current_root)
        if current_root_path == leftover_dir:
            dirnames[:] = []
            continue
        visible_dirnames: list[str] = []
        for dirname in dirnames:
            candidate_dir = current_root_path / dirname
            if _normalized_path_key(candidate_dir).startswith(_normalized_path_key(leftover_dir)):
                continue
            visible_dirnames.append(dirname)
        dirnames[:] = visible_dirnames
        for filename in sorted(filenames):
            candidate = current_root_path / filename
            if _normalized_path_key(candidate).startswith(_normalized_path_key(leftover_dir)):
                continue
            if candidate.is_file():
                files.append(candidate)
    files.sort(key=lambda item: (_normalized_path_key(item.parent), _normalized_path_key(item)))
    return files


def resolve_leftover_target(leftover_dir: Path, file_name: str) -> tuple[Path, bool]:
    """Resolve target path in leftover dir, handling name collisions with __2, __3 suffix."""
    candidate = leftover_dir / file_name
    if not candidate.exists():
        return candidate, False

    path_obj = Path(file_name)
    stem = path_obj.stem
    suffix = path_obj.suffix
    index = 2
    while True:
        candidate = leftover_dir / f"{stem}__{index}{suffix}"
        if not candidate.exists():
            return candidate, True
        index += 1


def remove_empty_directories(source_root: Path, leftover_dir_name: str) -> list[Path]:
    """Remove empty subdirectories under source_root, excluding the leftover dir itself."""
    leftover_dir = source_root / leftover_dir_name
    removed: list[Path] = []
    for current_root, dirnames, filenames in os.walk(source_root, topdown=False):
        current_root_path = Path(current_root)
        if current_root_path == source_root:
            continue
        if current_root_path == leftover_dir:
            continue
        if _normalized_path_key(current_root_path).startswith(_normalized_path_key(leftover_dir)):
            continue
        if dirnames or filenames:
            continue
        try:
            current_root_path.rmdir()
        except OSError:
            continue
        removed.append(current_root_path)
    removed.sort(key=lambda item: _normalized_path_key(item))
    return removed


def execute_leftover_consolidation(
    source_dirs: tuple[Path, ...],
    leftover_dir_name: str = "_remaining_files",
) -> LeftoverConsolidationResult:
    """Consolidate leftover files from source directories into a leftover folder per source.

    After an organize/rename operation, remaining files in each source directory
    are moved into a single leftover folder. Empty directories are then removed.
    All operations are journaled for undo support.
    """
    result = LeftoverConsolidationResult(directory_name=leftover_dir_name)
    for source_root in source_dirs:
        leftover_dir = source_root / leftover_dir_name
        candidate_files = discover_leftover_files(source_root, leftover_dir_name)
        if not candidate_files:
            continue
        for candidate in candidate_files:
            try:
                leftover_dir.mkdir(parents=True, exist_ok=True)
                target_path, conflict_resolved = resolve_leftover_target(leftover_dir, candidate.name)
                shutil.move(str(candidate), str(target_path))
                result.entries.append(
                    LeftoverConsolidationEntry(
                        source_root=source_root,
                        source_path=candidate,
                        target_path=target_path,
                        conflict_resolved=conflict_resolved,
                    )
                )
            except Exception as exc:  # pragma: no cover
                result.errors.append(str(exc))
        result.removed_empty_directories.extend(
            remove_empty_directories(source_root, leftover_dir_name)
        )
    return result


def build_leftover_journal_entries(
    result: LeftoverConsolidationResult,
) -> list[dict[str, object]]:
    """Build journal entries for leftover consolidation, suitable for undo."""
    entries: list[dict[str, object]] = []
    for item in result.entries:
        entries.append(
            {
                "source_path": str(item.source_path),
                "target_path": str(item.target_path),
                "outcome": "leftover-consolidated",
                "reason": "moved source leftover into the consolidation directory",
                "reversible": True,
                "undo_action": "move_back",
                "undo_from_path": str(item.target_path),
                "undo_to_path": str(item.source_path),
                "leftover_consolidation": True,
                "source_root": str(item.source_root),
            }
        )
    return entries
