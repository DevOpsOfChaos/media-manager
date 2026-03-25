from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import shutil
from typing import Callable, Iterable, Literal

from media_manager.constants import DEFAULT_NO_DATE_DIR, DEFAULT_TEMPLATE, GERMAN_MONTHS, MEDIA_EXTENSIONS
from media_manager.exiftool import ExifToolClient, pick_best_date

Mode = Literal["copy", "move"]


@dataclass(slots=True)
class MediaDecision:
    source: Path
    destination: Path
    action: Mode
    date_source: str
    date_value: str | None


@dataclass(slots=True)
class OrganizeSummary:
    total_files: int = 0
    applied_files: int = 0
    skipped_files: int = 0
    no_date_files: int = 0
    errors: int = 0


def iter_media_files(source_dir: Path) -> Iterable[Path]:
    for path in source_dir.rglob("*"):
        if path.is_file() and path.suffix.lower() in MEDIA_EXTENSIONS:
            yield path


def unique_destination(path: Path) -> Path:
    if not path.exists():
        return path

    counter = 1
    while True:
        candidate = path.with_name(f"{path.stem}_{counter}{path.suffix}")
        if not candidate.exists():
            return candidate
        counter += 1


def build_relative_target(dt: datetime, extension: str, template: str = DEFAULT_TEMPLATE) -> Path:
    rendered = template.format(
        year=f"{dt.year:04d}",
        month_num=f"{dt.month:02d}",
        month_name=GERMAN_MONTHS[dt.month],
        day=f"{dt.day:02d}",
        hour=f"{dt.hour:02d}",
        minute=f"{dt.minute:02d}",
        ext=extension.lstrip(".").lower(),
    )
    return Path(rendered)


def build_decision(
    file_path: Path,
    target_root: Path,
    exiftool: ExifToolClient,
    template: str = DEFAULT_TEMPLATE,
    action: Mode = "copy",
    fallback_to_file_time: bool = True,
) -> MediaDecision:
    metadata = exiftool.read_metadata(file_path)
    dt, used_key, used_value = pick_best_date(metadata)

    date_source = "metadata"
    date_value = str(used_value) if used_value is not None else None

    if dt is None and fallback_to_file_time:
        dt = datetime.fromtimestamp(file_path.stat().st_mtime)
        date_source = "filesystem"
        date_value = dt.isoformat(sep=" ", timespec="seconds")

    if dt is None:
        relative_dir = Path(DEFAULT_NO_DATE_DIR)
        date_source = "missing"
    else:
        relative_dir = build_relative_target(dt, file_path.suffix, template=template)

    destination = unique_destination(target_root / relative_dir / file_path.name)

    if used_key and date_source == "metadata":
        date_source = used_key

    return MediaDecision(
        source=file_path,
        destination=destination,
        action=action,
        date_source=date_source,
        date_value=date_value,
    )


def apply_decision(decision: MediaDecision) -> None:
    decision.destination.parent.mkdir(parents=True, exist_ok=True)
    if decision.action == "copy":
        shutil.copy2(decision.source, decision.destination)
    else:
        shutil.move(str(decision.source), str(decision.destination))


def organize(
    source_dir: Path,
    target_dir: Path,
    exiftool: ExifToolClient,
    template: str = DEFAULT_TEMPLATE,
    action: Mode = "copy",
    apply_changes: bool = False,
    fallback_to_file_time: bool = True,
    on_decision: Callable[[MediaDecision], None] | None = None,
    on_error: Callable[[Path, Exception], None] | None = None,
    on_info: Callable[[str], None] | None = None,
) -> OrganizeSummary:
    summary = OrganizeSummary()

    files = list(iter_media_files(source_dir))
    summary.total_files = len(files)

    for file_path in files:
        try:
            decision = build_decision(
                file_path=file_path,
                target_root=target_dir,
                exiftool=exiftool,
                template=template,
                action=action,
                fallback_to_file_time=fallback_to_file_time,
            )
        except Exception as exc:
            summary.errors += 1
            if on_error:
                on_error(file_path, exc)
            else:
                print(f"FEHLER: {file_path} -> {exc}")
            continue

        if decision.date_source == "missing":
            summary.no_date_files += 1

        if on_decision:
            on_decision(decision)
        else:
            print(f"{decision.action.upper()}: {decision.source} -> {decision.destination}")
            print(f"  Datumsquelle: {decision.date_source}")
            if decision.date_value:
                print(f"  Datumswert:   {decision.date_value}")

        if apply_changes:
            apply_decision(decision)
            summary.applied_files += 1
            if on_info:
                on_info(f"Ausgeführt: {decision.source.name}")
        else:
            summary.skipped_files += 1

    return summary
