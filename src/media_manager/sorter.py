from __future__ import annotations

import shutil
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

from .constants import MEDIA_EXTENSIONS
from .dates import resolve_media_datetime

ProgressCallback = Callable[[str], None]


@dataclass(slots=True)
class SortConfig:
    source_dirs: list[Path]
    target_dir: Path
    target_template: str = "{year}/{month}"
    dry_run: bool = True
    mode: str = "copy"
    exiftool_path: Path | None = None


@dataclass(slots=True)
class SortEntry:
    source: Path
    target: Path | None
    action: str
    reason: str = ""


@dataclass(slots=True)
class SortResult:
    processed: int = 0
    organized: int = 0
    skipped: int = 0
    errors: int = 0
    entries: list[SortEntry] = field(default_factory=list)


def is_media_file(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() in MEDIA_EXTENSIONS


def build_target_dir(base_target: Path, media_dt, template: str) -> Path:
    rendered = template.format(
        year=f"{media_dt.year:04d}",
        month=f"{media_dt.month:02d}",
        day=f"{media_dt.day:02d}",
    )
    return base_target / rendered


def ensure_unique_path(path: Path) -> Path:
    if not path.exists():
        return path
    counter = 1
    while True:
        candidate = path.with_name(f"{path.stem}_{counter}{path.suffix}")
        if not candidate.exists():
            return candidate
        counter += 1


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


def _emit_progress(progress_callback: ProgressCallback | None, message: str) -> None:
    if progress_callback is not None:
        progress_callback(message)


def organize_media(config: SortConfig, progress_callback: ProgressCallback | None = None) -> SortResult:
    result = SortResult()

    _emit_progress(progress_callback, "Scanning source folders ...")
    media_files = iter_media_files(config.source_dirs)
    total_files = len(media_files)
    file_label = "file" if total_files == 1 else "files"
    _emit_progress(progress_callback, f"Found {total_files} media {file_label}.")

    for index, file_path in enumerate(media_files, start=1):
        result.processed += 1
        _emit_progress(progress_callback, f"Processing {index}/{total_files}: {file_path.name}")

        try:
            media_dt = resolve_media_datetime(file_path, exiftool_path=config.exiftool_path)
            target_dir = build_target_dir(config.target_dir, media_dt, config.target_template)
            target_path = ensure_unique_path(target_dir / file_path.name)

            action = "preview-copy" if config.mode == "copy" else "preview-move"
            if not config.dry_run:
                target_dir.mkdir(parents=True, exist_ok=True)
                if config.mode == "move":
                    shutil.move(str(file_path), str(target_path))
                    action = "moved"
                else:
                    shutil.copy2(file_path, target_path)
                    action = "copied"

            result.organized += 1
            result.entries.append(
                SortEntry(
                    source=file_path,
                    target=target_path,
                    action=action,
                )
            )
        except Exception as exc:  # pragma: no cover - safeguard for runtime
            result.errors += 1
            result.entries.append(
                SortEntry(
                    source=file_path,
                    target=None,
                    action="error",
                    reason=str(exc),
                )
            )

    _emit_progress(
        progress_callback,
        f"Finished. {result.organized} action(s), {result.errors} error(s).",
    )
    return result
