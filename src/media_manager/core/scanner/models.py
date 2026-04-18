from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True, frozen=True)
class ScanOptions:
    source_dirs: tuple[Path, ...]
    recursive: bool = True
    include_hidden: bool = False
    follow_symlinks: bool = False
    media_extensions: frozenset[str] | None = None


@dataclass(slots=True, frozen=True)
class ScannedFile:
    source_root: Path
    path: Path
    relative_path: Path
    extension: str
    size_bytes: int


@dataclass(slots=True)
class ScanSummary:
    source_dirs: tuple[Path, ...]
    files: list[ScannedFile] = field(default_factory=list)
    missing_sources: list[Path] = field(default_factory=list)
    skipped_hidden_paths: int = 0
    skipped_non_media_files: int = 0

    @property
    def source_count(self) -> int:
        return len(self.source_dirs)

    @property
    def media_file_count(self) -> int:
        return len(self.files)

    @property
    def total_size_bytes(self) -> int:
        return sum(item.size_bytes for item in self.files)
