from __future__ import annotations

import os
from pathlib import Path

from media_manager.core.date_resolver import resolve_capture_datetime
from media_manager.core.scanner import ScanOptions, scan_media_sources

from .models import OrganizeDryRun, OrganizePlanEntry, OrganizePlannerOptions
from .patterns import render_organize_directory


def _normalized_path_key(path: Path) -> str:
    return os.path.normcase(str(path))


def build_organize_dry_run(options: OrganizePlannerOptions) -> OrganizeDryRun:
    scan_summary = scan_media_sources(
        ScanOptions(
            source_dirs=options.source_dirs,
            recursive=options.recursive,
            include_hidden=options.include_hidden,
            follow_symlinks=options.follow_symlinks,
        )
    )
    dry_run = OrganizeDryRun(options=options, scan_summary=scan_summary)

    for scanned_file in scan_summary.files:
        try:
            resolution = resolve_capture_datetime(
                scanned_file.path,
                exiftool_path=options.exiftool_path,
            )
            target_relative_dir = render_organize_directory(
                options.pattern,
                resolution,
                source_root=scanned_file.source_root,
            )
            target_path = options.target_root / target_relative_dir / scanned_file.path.name
        except Exception as exc:
            dry_run.entries.append(
                OrganizePlanEntry(
                    scanned_file=scanned_file,
                    resolution=None,
                    operation_mode=options.operation_mode,
                    status="error",
                    reason=str(exc),
                    target_relative_dir=None,
                    target_path=None,
                )
            )
            continue

        source_key = _normalized_path_key(scanned_file.path)
        target_key = _normalized_path_key(target_path)

        if source_key == target_key:
            dry_run.entries.append(
                OrganizePlanEntry(
                    scanned_file=scanned_file,
                    resolution=resolution,
                    operation_mode=options.operation_mode,
                    status="skipped",
                    reason="source already matches the planned target path",
                    target_relative_dir=target_relative_dir,
                    target_path=target_path,
                )
            )
            continue

        if target_path.exists():
            dry_run.entries.append(
                OrganizePlanEntry(
                    scanned_file=scanned_file,
                    resolution=resolution,
                    operation_mode=options.operation_mode,
                    status="conflict",
                    reason="target path already exists",
                    target_relative_dir=target_relative_dir,
                    target_path=target_path,
                )
            )
            continue

        dry_run.entries.append(
            OrganizePlanEntry(
                scanned_file=scanned_file,
                resolution=resolution,
                operation_mode=options.operation_mode,
                status="planned",
                reason="ready for organize dry-run output",
                target_relative_dir=target_relative_dir,
                target_path=target_path,
            )
        )

    collisions: dict[str, list[OrganizePlanEntry]] = {}
    for entry in dry_run.entries:
        if entry.status != "planned" or entry.target_path is None:
            continue
        collisions.setdefault(_normalized_path_key(entry.target_path), []).append(entry)

    for entries in collisions.values():
        if len(entries) < 2:
            continue
        for entry in entries:
            entry.status = "conflict"
            entry.reason = "multiple source files would resolve to the same target path"

    dry_run.entries.sort(key=lambda item: _normalized_path_key(item.source_path))
    return dry_run
