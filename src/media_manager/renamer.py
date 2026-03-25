from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

from .dates import resolve_media_datetime
from .sorter import iter_media_files

ProgressCallback = Callable[[str], None]
INVALID_FILENAME_CHARS = '<>:"/\\|?*'


@dataclass(slots=True)
class RenameConfig:
    source_dirs: list[Path]
    template: str
    dry_run: bool = True
    exiftool_path: Path | None = None


@dataclass(slots=True)
class RenameEntry:
    source: Path
    target: Path | None
    action: str
    reason: str = ""


@dataclass(slots=True)
class RenameResult:
    processed: int = 0
    renamed: int = 0
    skipped: int = 0
    errors: int = 0
    entries: list[RenameEntry] = field(default_factory=list)


def sanitize_filename(value: str) -> str:
    cleaned = value.strip()
    for char in INVALID_FILENAME_CHARS:
        cleaned = cleaned.replace(char, "_")
    cleaned = cleaned.replace("\n", "_").replace("\r", "_")
    return cleaned.strip(" .")


def render_rename_filename(file_path: Path, media_dt, template: str, index: int) -> str:
    rendered = template.format(
        year=f"{media_dt.year:04d}",
        month=f"{media_dt.month:02d}",
        day=f"{media_dt.day:02d}",
        hour=f"{media_dt.hour:02d}",
        minute=f"{media_dt.minute:02d}",
        second=f"{media_dt.second:02d}",
        stem=sanitize_filename(file_path.stem),
        suffix=file_path.suffix,
        index=f"{index:04d}",
    )
    cleaned = sanitize_filename(rendered)
    if not cleaned:
        cleaned = f"{media_dt.year:04d}{media_dt.month:02d}{media_dt.day:02d}_{media_dt.hour:02d}{media_dt.minute:02d}{media_dt.second:02d}_{sanitize_filename(file_path.stem)}"
    if "{suffix}" not in template and not cleaned.lower().endswith(file_path.suffix.lower()):
        cleaned += file_path.suffix
    return cleaned


def ensure_unique_rename_target(target_path: Path, source_path: Path, reserved_targets: set[Path]) -> Path:
    if target_path == source_path:
        reserved_targets.add(target_path)
        return target_path
    if target_path not in reserved_targets and not target_path.exists():
        reserved_targets.add(target_path)
        return target_path

    counter = 1
    while True:
        candidate = target_path.with_name(f"{target_path.stem}_{counter}{target_path.suffix}")
        if candidate not in reserved_targets and not candidate.exists():
            reserved_targets.add(candidate)
            return candidate
        counter += 1


def _emit_progress(progress_callback: ProgressCallback | None, message: str) -> None:
    if progress_callback is not None:
        progress_callback(message)


def rename_media(config: RenameConfig, progress_callback: ProgressCallback | None = None) -> RenameResult:
    result = RenameResult()
    reserved_targets: set[Path] = set()

    _emit_progress(progress_callback, "Scanning source folders for rename ...")
    media_files = iter_media_files(config.source_dirs)
    total_files = len(media_files)
    file_label = "file" if total_files == 1 else "files"
    _emit_progress(progress_callback, f"Found {total_files} media {file_label}.")

    for index, file_path in enumerate(media_files, start=1):
        result.processed += 1
        _emit_progress(progress_callback, f"Renaming {index}/{total_files}: {file_path.name}")
        try:
            media_dt = resolve_media_datetime(file_path, exiftool_path=config.exiftool_path)
            new_name = render_rename_filename(file_path, media_dt, config.template, index)
            target_path = ensure_unique_rename_target(file_path.with_name(new_name), file_path, reserved_targets)

            if target_path == file_path:
                result.skipped += 1
                result.entries.append(
                    RenameEntry(source=file_path, target=file_path, action="unchanged", reason="Name already matches")
                )
                continue

            action = "preview-rename"
            if not config.dry_run:
                file_path.rename(target_path)
                action = "renamed"

            result.renamed += 1
            result.entries.append(RenameEntry(source=file_path, target=target_path, action=action))
        except Exception as exc:  # pragma: no cover - runtime safeguard
            result.errors += 1
            result.entries.append(RenameEntry(source=file_path, target=None, action="error", reason=str(exc)))

    _emit_progress(progress_callback, f"Finished. {result.renamed} rename action(s), {result.errors} error(s).")
    return result
