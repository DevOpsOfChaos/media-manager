from __future__ import annotations

import os
from pathlib import Path

from media_manager.core.date_resolver import resolve_capture_datetime
from media_manager.core.scanner import ScanOptions, scan_media_sources

from .models import RenameDryRun, RenamePlanEntry, RenamePlannerOptions
from .templates import render_rename_filename


def _normalized_path_key(path: Path) -> str:
    return os.path.normcase(str(path))


def build_rename_dry_run(options: RenamePlannerOptions) -> RenameDryRun:
    scan_summary = scan_media_sources(
        ScanOptions(
            source_dirs=options.source_dirs,
            recursive=options.recursive,
            include_hidden=options.include_hidden,
            follow_symlinks=options.follow_symlinks,
        )
    )
    dry_run = RenameDryRun(options=options, scan_summary=scan_summary)

    for index, scanned_file in enumerate(scan_summary.files, start=1):
        try:
            resolution = resolve_capture_datetime(
                scanned_file.path,
                exiftool_path=options.exiftool_path,
            )
            rendered_name = render_rename_filename(
                scanned_file.path,
                resolution,
                options.template,
                index=index,
                source_root=scanned_file.source_root,
            )
            target_path = scanned_file.path.with_name(rendered_name)
        except Exception as exc:
            dry_run.entries.append(
                RenamePlanEntry(
                    scanned_file=scanned_file,
                    resolution=None,
                    status="error",
                    reason=str(exc),
                    rendered_name=None,
                    target_path=None,
                )
            )
            continue

        source_key = _normalized_path_key(scanned_file.path)
        target_key = _normalized_path_key(target_path)

        if source_key == target_key:
            dry_run.entries.append(
                RenamePlanEntry(
                    scanned_file=scanned_file,
                    resolution=resolution,
                    status="skipped",
                    reason="source file already matches the planned rename target",
                    rendered_name=rendered_name,
                    target_path=target_path,
                )
            )
            continue

        if target_path.exists():
            dry_run.entries.append(
                RenamePlanEntry(
                    scanned_file=scanned_file,
                    resolution=resolution,
                    status="conflict",
                    reason="target file name already exists in the source directory",
                    rendered_name=rendered_name,
                    target_path=target_path,
                )
            )
            continue

        dry_run.entries.append(
            RenamePlanEntry(
                scanned_file=scanned_file,
                resolution=resolution,
                status="planned",
                reason="ready for rename dry-run output",
                rendered_name=rendered_name,
                target_path=target_path,
            )
        )

    collisions: dict[str, list[RenamePlanEntry]] = {}
    for entry in dry_run.entries:
        if entry.status != "planned" or entry.target_path is None:
            continue
        collisions.setdefault(_normalized_path_key(entry.target_path), []).append(entry)

    for entries in collisions.values():
        if len(entries) < 2:
            continue
        for entry in entries:
            entry.status = "conflict"
            entry.reason = "multiple source files would resolve to the same target file name"

    dry_run.entries.sort(key=lambda item: _normalized_path_key(item.source_path))
    return dry_run
