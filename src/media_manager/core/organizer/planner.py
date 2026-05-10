from __future__ import annotations

import os
from pathlib import Path

from media_manager.core.date_resolver import resolve_capture_datetime
from media_manager.core.file_identity import files_have_identical_content
from media_manager.core.media_groups import build_media_groups
from media_manager.core.path_filters import path_is_included_by_patterns
from media_manager.core.scanner import ScanOptions, scan_media_sources
from media_manager.core.scanner.models import ScannedFile

from .models import OrganizeDryRun, OrganizePlanEntry, OrganizePlannerOptions
from .patterns import render_organize_directory

_ASSOCIATED_SIDECAR_EXTENSIONS = frozenset({".xmp", ".aae"})


def _normalized_path_key(path: Path) -> str:
    return os.path.normcase(str(path))


def _build_group_target_paths(entry_target_dir: Path, target_root: Path, *, source_paths: list[Path]) -> dict[Path, Path]:
    return {
        source_path: target_root / entry_target_dir / source_path.name
        for source_path in source_paths
    }


def _evaluate_group_plan_state(group_target_paths: dict[Path, Path], *, conflict_policy: str = "conflict") -> tuple[str, str]:
    if not group_target_paths:
        return "error", "missing target path"

    normalized_pairs = [
        (source_path, target_path, _normalized_path_key(source_path), _normalized_path_key(target_path))
        for source_path, target_path in group_target_paths.items()
    ]

    same_path_count = sum(1 for _, _, source_key, target_key in normalized_pairs if source_key == target_key)
    if same_path_count == len(normalized_pairs):
        return "skipped", "source already matches the planned target path"
    if same_path_count > 0:
        return "conflict", "one or more group members already match the planned target path"

    existing_count = 0
    identical_count = 0
    for source_path, target_path, _, _ in normalized_pairs:
        if not target_path.exists():
            continue
        existing_count += 1
        if files_have_identical_content(source_path, target_path):
            identical_count += 1
        else:
            if conflict_policy == "skip":
                return "skipped", "target path already exists; skipped by conflict policy"
            return "conflict", "target path already exists"

    if existing_count:
        if identical_count == len(normalized_pairs):
            return "skipped", "target already exists with identical file content"
        if conflict_policy == "skip":
            return "skipped", "one or more target paths already exist; skipped by conflict policy"
        return "conflict", "one or more target paths already exist"

    return "planned", "ready for organize execution"


def _augment_files_with_associated_sidecars(
    files: list[ScannedFile],
    *,
    exclude_patterns: tuple[str, ...] = (),
) -> list[ScannedFile]:
    augmented: list[ScannedFile] = list(files)
    seen_paths = {_normalized_path_key(item.path) for item in files}

    for item in files:
        parent = item.path.parent
        stem = item.path.stem
        for extension in sorted(_ASSOCIATED_SIDECAR_EXTENSIONS):
            candidate = parent / f"{stem}{extension}"
            candidate_key = _normalized_path_key(candidate)
            if candidate_key in seen_paths:
                continue
            if not candidate.exists() or not candidate.is_file():
                continue
            if exclude_patterns and not path_is_included_by_patterns(
                candidate,
                include_patterns=(),
                exclude_patterns=exclude_patterns,
                source_root=item.source_root,
            ):
                continue
            try:
                size_bytes = candidate.stat().st_size
            except OSError:
                size_bytes = 0
            augmented.append(
                ScannedFile(
                    source_root=item.source_root,
                    path=candidate,
                    relative_path=candidate.relative_to(item.source_root),
                    extension=extension,
                    size_bytes=size_bytes,
                )
            )
            seen_paths.add(candidate_key)

    augmented.sort(key=lambda entry: (_normalized_path_key(entry.source_root), _normalized_path_key(entry.path)))
    return augmented


def build_organize_dry_run(options: OrganizePlannerOptions, progress_callback=None) -> OrganizeDryRun:
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
        raise ValueError("Organize conflict policy must be one of: conflict, skip.")

    dry_run = OrganizeDryRun(options=options, scan_summary=scan_summary)

    scanned_files = list(scan_summary.files)
    total = len(scanned_files)
    if options.include_associated_files:
        scanned_files = _augment_files_with_associated_sidecars(
            scanned_files,
            exclude_patterns=options.exclude_patterns,
        )

    scanned_by_path = {item.path: item for item in scanned_files}
    idx = 0
    if options.include_associated_files:
        groups = build_media_groups(scanned_files)
        for group in groups:
            scanned_file = scanned_by_path[group.main_path]
            try:
                resolution = resolve_capture_datetime(scanned_file.path, exiftool_path=options.exiftool_path)
                target_relative_dir = render_organize_directory(options.pattern, resolution, source_root=scanned_file.source_root)
                group_target_paths = _build_group_target_paths(
                    target_relative_dir,
                    options.target_root,
                    source_paths=[member.path for member in group.members],
                )
                target_path = group_target_paths[scanned_file.path]
                status, reason = _evaluate_group_plan_state(group_target_paths, conflict_policy=options.conflict_policy)
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
                        media_group=group,
                        group_target_paths={},
                    )
                )
                idx += 1
                if progress_callback: progress_callback(idx, total)
                continue

            dry_run.entries.append(
                OrganizePlanEntry(
                    scanned_file=scanned_file,
                    resolution=resolution,
                    operation_mode=options.operation_mode,
                    status=status,
                    reason=reason,
                    target_relative_dir=target_relative_dir,
                    target_path=target_path,
                    media_group=group,
                    group_target_paths=group_target_paths,
                )
            )
            idx += 1
            if progress_callback: progress_callback(idx, total)
    else:
        for scanned_file in scan_summary.files:
            try:
                resolution = resolve_capture_datetime(scanned_file.path, exiftool_path=options.exiftool_path)
                target_relative_dir = render_organize_directory(options.pattern, resolution, source_root=scanned_file.source_root)
                target_path = options.target_root / target_relative_dir / scanned_file.path.name
                group_target_paths = {scanned_file.path: target_path}
                status, reason = _evaluate_group_plan_state(group_target_paths, conflict_policy=options.conflict_policy)
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
                        media_group=None,
                        group_target_paths={},
                    )
                )
                idx += 1
                if progress_callback: progress_callback(idx, total)
                continue

            dry_run.entries.append(
                OrganizePlanEntry(
                    scanned_file=scanned_file,
                    resolution=resolution,
                    operation_mode=options.operation_mode,
                    status=status,
                    reason=reason,
                    target_relative_dir=target_relative_dir,
                    target_path=target_path,
                    media_group=None,
                    group_target_paths=group_target_paths,
                )
            )
            idx += 1
            if progress_callback: progress_callback(idx, total)

    collisions: dict[str, list[OrganizePlanEntry]] = {}
    for entry in dry_run.entries:
        if entry.status != "planned":
            continue
        for target_path in entry.group_target_paths.values():
            collisions.setdefault(_normalized_path_key(target_path), []).append(entry)

    for entries in collisions.values():
        seen_ids: set[int] = set()
        unique_count = len({id(item) for item in entries})
        if unique_count < 2:
            continue
        for entry in entries:
            key = id(entry)
            if key in seen_ids:
                continue
            seen_ids.add(key)
            entry.status = "conflict"
            entry.reason = "multiple source files would resolve to the same target path"

    dry_run.entries.sort(key=lambda item: _normalized_path_key(item.source_path))
    return dry_run
