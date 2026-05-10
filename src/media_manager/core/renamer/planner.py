from __future__ import annotations

import os
from pathlib import Path

from media_manager.core.date_resolver import resolve_capture_datetime
from media_manager.core.media_groups import build_media_groups, summarize_media_groups
from media_manager.core.metadata.inspect import inspect_media_files_batch
from media_manager.core.metadata.models import FileInspection
from media_manager.core.path_filters import path_is_included_by_patterns
from media_manager.core.scanner import ScanOptions, scan_media_sources
from media_manager.core.scanner.models import ScannedFile

from .models import RenameDryRun, RenameMemberTarget, RenamePlanEntry, RenamePlannerOptions
from .templates import render_rename_filename

_ASSOCIATED_SIDECAR_EXTENSIONS = (".xmp", ".aae")


def _normalized_path_key(path) -> str:
    return os.path.normcase(str(path))


def _build_scanned_file(path: Path, source_root: Path) -> ScannedFile:
    try:
        size_bytes = path.stat().st_size
    except OSError:
        size_bytes = 0
    return ScannedFile(
        source_root=source_root,
        path=path,
        relative_path=path.relative_to(source_root),
        extension=path.suffix.lower(),
        size_bytes=size_bytes,
    )


def _augment_with_sidecar_siblings(
    files: list[ScannedFile],
    *,
    exclude_patterns: tuple[str, ...] = (),
) -> list[ScannedFile]:
    augmented: list[ScannedFile] = list(files)
    seen = {_normalized_path_key(item.path) for item in files}
    for scanned_file in list(files):
        stem = scanned_file.path.stem
        parent = scanned_file.path.parent
        for ext in _ASSOCIATED_SIDECAR_EXTENSIONS:
            candidate = parent / f"{stem}{ext}"
            key = _normalized_path_key(candidate)
            if key in seen or not candidate.exists() or not candidate.is_file():
                continue
            if exclude_patterns and not path_is_included_by_patterns(
                candidate,
                include_patterns=(),
                exclude_patterns=exclude_patterns,
                source_root=scanned_file.source_root,
            ):
                continue
            seen.add(key)
            augmented.append(_build_scanned_file(candidate, scanned_file.source_root))
    augmented.sort(key=lambda item: (str(item.source_root).lower(), str(item.relative_path).lower()))
    return augmented


def _single_plan_entry(options: RenamePlannerOptions, scanned_file: ScannedFile, index: int, *, inspection: FileInspection | None = None) -> RenamePlanEntry:
    try:
        resolution = resolve_capture_datetime(scanned_file.path, inspection=inspection, exiftool_path=options.exiftool_path)
        rendered_name = render_rename_filename(
            scanned_file.path,
            resolution,
            options.template,
            index=index,
            source_root=scanned_file.source_root,
        )
        target_path = scanned_file.path.with_name(rendered_name)
    except Exception as exc:
        return RenamePlanEntry(
            scanned_file=scanned_file,
            resolution=None,
            status="error",
            reason=str(exc),
            rendered_name=None,
            target_path=None,
            group_id=f"single:{_normalized_path_key(scanned_file.path)}",
        )

    source_key = _normalized_path_key(scanned_file.path)
    target_key = _normalized_path_key(target_path)
    if source_key == target_key:
        status = "skipped"
        reason = "source file already matches the planned rename target"
    elif target_path.exists():
        if options.conflict_policy == "skip":
            status = "skipped"
            reason = "target file name already exists in the source directory; skipped by conflict policy"
        else:
            status = "conflict"
            reason = "target file name already exists in the source directory"
    else:
        status = "planned"
        reason = "ready for rename execution"

    return RenamePlanEntry(
        scanned_file=scanned_file,
        resolution=resolution,
        status=status,
        reason=reason,
        rendered_name=rendered_name,
        target_path=target_path,
        group_id=f"single:{_normalized_path_key(scanned_file.path)}",
        group_kind="single",
        associated_paths=(),
        association_warnings=(),
        member_targets=(RenameMemberTarget(source_path=scanned_file.path, target_path=target_path, role="main"),) if target_path is not None else (),
    )


def _group_plan_entry(options: RenamePlannerOptions, group, scanned_index: dict[str, ScannedFile], index: int) -> RenamePlanEntry:
    main_scanned = scanned_index[_normalized_path_key(group.main_path)]
    try:
        resolution = resolve_capture_datetime(group.main_path, exiftool_path=options.exiftool_path)
        rendered_name = render_rename_filename(
            group.main_path,
            resolution,
            options.template,
            index=index,
            source_root=group.source_root,
        )
        rendered_stem = Path(rendered_name).stem
        main_target_path = group.main_path.with_name(rendered_name)
    except Exception as exc:
        return RenamePlanEntry(
            scanned_file=main_scanned,
            resolution=None,
            status="error",
            reason=str(exc),
            rendered_name=None,
            target_path=None,
            group_id=group.group_id,
            group_kind=group.group_kind,
            associated_paths=group.associated_paths,
            association_warnings=group.association_warnings,
        )

    member_targets = [RenameMemberTarget(source_path=group.main_path, target_path=main_target_path, role="main")]
    for member in group.members:
        if member.path == group.main_path:
            continue
        member_target = member.path.with_name(f"{rendered_stem}{member.path.suffix}")
        member_targets.append(RenameMemberTarget(source_path=member.path, target_path=member_target, role=member.role))

    all_match = all(_normalized_path_key(item.source_path) == _normalized_path_key(item.target_path) for item in member_targets)
    if all_match:
        status = "skipped"
        reason = "source file group already matches the planned rename target"
    else:
        conflict_target = next(
            (
                item.target_path
                for item in member_targets
                if _normalized_path_key(item.source_path) != _normalized_path_key(item.target_path) and item.target_path.exists()
            ),
            None,
        )
        if conflict_target is not None:
            if options.conflict_policy == "skip":
                status = "skipped"
                reason = "target file name already exists in the source directory; skipped by conflict policy"
            else:
                status = "conflict"
                reason = "target file name already exists in the source directory"
        else:
            status = "planned"
            reason = "ready for rename execution"

    return RenamePlanEntry(
        scanned_file=main_scanned,
        resolution=resolution,
        status=status,
        reason=reason,
        rendered_name=rendered_name,
        target_path=main_target_path,
        group_id=group.group_id,
        group_kind=group.group_kind,
        associated_paths=group.associated_paths,
        association_warnings=group.association_warnings,
        member_targets=tuple(member_targets),
    )


def build_rename_dry_run(options: RenamePlannerOptions, progress_callback=None, cancel_event=None) -> RenameDryRun:
    scan_summary = scan_media_sources(
        ScanOptions(
            source_dirs=options.source_dirs,
            recursive=options.recursive,
            include_hidden=options.include_hidden,
            follow_symlinks=options.follow_symlinks,
            include_patterns=options.include_patterns,
            exclude_patterns=options.exclude_patterns,
        )
    )
    if options.conflict_policy not in {"conflict", "skip"}:
        raise ValueError("Rename conflict policy must be one of: conflict, skip.")

    dry_run = RenameDryRun(options=options, scan_summary=scan_summary)
    total = len(scan_summary.files)
    batch_size = options.batch_size if options.batch_size > 0 else total

    if not options.include_associated_files:
        file_list = list(scan_summary.files)
        total = len(file_list)
        file_paths = [item.path for item in file_list]

        for batch_start in range(0, total, batch_size):
            if cancel_event and cancel_event.is_set():
                break

            batch_end = min(batch_start + batch_size, total)
            batch_paths = file_paths[batch_start:batch_end]
            batch_inspections = inspect_media_files_batch(
                batch_paths, exiftool_path=options.exiftool_path,
            )

            for i in range(batch_start, batch_end):
                scanned_file = file_list[i]
                inspection = batch_inspections.get(scanned_file.path)
                index = i + 1
                dry_run.entries.append(
                    _single_plan_entry(options, scanned_file, index, inspection=inspection)
                )

            if progress_callback:
                progress_callback(batch_end, total)
    else:
        augmented_files = _augment_with_sidecar_siblings(
            list(scan_summary.files),
            exclude_patterns=options.exclude_patterns,
        )
        groups = build_media_groups(augmented_files)
        summary = summarize_media_groups(groups)
        dry_run.media_group_count = summary.group_count
        dry_run.associated_file_count = summary.associated_file_count
        dry_run.association_warning_count = summary.association_warning_count
        dry_run.group_kind_summary = dict(summary.group_kind_summary)
        scanned_index = {_normalized_path_key(item.path): item for item in augmented_files}
        for index, group in enumerate(groups, start=1):
            if cancel_event and cancel_event.is_set():
                break
            dry_run.entries.append(_group_plan_entry(options, group, scanned_index, index=index))
            if progress_callback and (index % batch_size == 0 or index == total):
                progress_callback(index, total)

    collisions: dict[str, list[RenamePlanEntry]] = {}
    for entry in dry_run.entries:
        if entry.status != "planned":
            continue
        member_targets = entry.member_targets or ((RenameMemberTarget(source_path=entry.source_path, target_path=entry.target_path, role="main"),) if entry.target_path is not None else ())
        for member_target in member_targets:
            collisions.setdefault(_normalized_path_key(member_target.target_path), []).append(entry)

    for entries in collisions.values():
        if len(entries) < 2:
            continue
        for entry in entries:
            entry.status = "conflict"
            entry.reason = "multiple source files would resolve to the same target file name"

    dry_run.entries.sort(key=lambda item: _normalized_path_key(item.source_path))
    if dry_run.media_group_count == 0:
        dry_run.media_group_count = len(dry_run.entries)
        dry_run.group_kind_summary = {"single": len(dry_run.entries)} if dry_run.entries else {}
    return dry_run
