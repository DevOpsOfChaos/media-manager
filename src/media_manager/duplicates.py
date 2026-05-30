from __future__ import annotations

import hashlib
import logging
from collections import Counter, defaultdict
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from media_manager.constants import SAMPLE_SIZE, HASH_CHUNK_SIZE

from .core.path_filters import path_is_included_by_patterns
from .core.perf_timer import timer
from .media_formats import media_kind_for_extension, normalize_extensions
from .sorter import iter_media_files
from .exiftool import read_exiftool_metadata_batch

_logger = logging.getLogger(__name__)

ProgressCallback = Callable[[str], None]


@dataclass(slots=True)
class DuplicateScanConfig:
    source_dirs: list[Path]
    sample_size: int = SAMPLE_SIZE
    hash_chunk_size: int = HASH_CHUNK_SIZE
    include_patterns: tuple[str, ...] = ()
    exclude_patterns: tuple[str, ...] = ()
    media_extensions: frozenset[str] | None = None


@dataclass(slots=True)
class ExactDuplicateGroup:
    files: list[Path]
    file_size: int
    sample_digest: str
    full_digest: str
    same_name: bool
    same_suffix: bool
    extension_summary: dict[str, int] = field(default_factory=dict)
    media_kind_summary: dict[str, int] = field(default_factory=dict)


@dataclass(slots=True)
class DuplicateScanResult:
    scanned_files: int = 0
    size_candidate_groups: int = 0
    size_candidate_files: int = 0
    sampled_files: int = 0
    hashed_files: int = 0
    exact_groups: list[ExactDuplicateGroup] = field(default_factory=list)
    exact_duplicate_files: int = 0
    exact_duplicates: int = 0
    errors: int = 0
    size_group_errors: int = 0
    sample_errors: int = 0
    hash_errors: int = 0
    compare_errors: int = 0
    skipped_filtered_files: int = 0
    extension_summary: dict[str, int] = field(default_factory=dict)
    media_kind_summary: dict[str, int] = field(default_factory=dict)
    image_file_count: int = 0
    raw_image_file_count: int = 0
    video_file_count: int = 0
    audio_file_count: int = 0
    unknown_media_kind_count: int = 0


def _emit_progress(progress_callback: ProgressCallback | None, message: str) -> None:
    if progress_callback is not None:
        progress_callback(message)


def _normalized_sort_key(path: Path) -> str:
    return str(path).lower()


def _extension_summary(paths: list[Path]) -> dict[str, int]:
    return dict(sorted(Counter(path.suffix.lower() for path in paths).items()))


def _media_kind_summary(paths: list[Path]) -> dict[str, int]:
    return dict(sorted(Counter(media_kind_for_extension(path.suffix) for path in paths).items()))


def _apply_scan_kind_summary(result: DuplicateScanResult, paths: list[Path]) -> None:
    result.extension_summary = _extension_summary(paths)
    result.media_kind_summary = _media_kind_summary(paths)
    result.image_file_count = result.media_kind_summary.get("image", 0)
    result.raw_image_file_count = result.media_kind_summary.get("raw-image", 0)
    result.video_file_count = result.media_kind_summary.get("video", 0)
    result.audio_file_count = result.media_kind_summary.get("audio", 0)
    result.unknown_media_kind_count = result.media_kind_summary.get("unknown", 0)


def _sample_offsets(file_size: int, sample_size: int) -> list[int]:
    if file_size <= sample_size * 3:
        return [0]

    offsets = [0, max(0, (file_size // 2) - (sample_size // 2)), max(0, file_size - sample_size)]
    unique_offsets: list[int] = []
    seen: set[int] = set()
    for offset in offsets:
        if offset in seen:
            continue
        seen.add(offset)
        unique_offsets.append(offset)
    return unique_offsets


def compute_sample_fingerprint(path: Path, sample_size: int = SAMPLE_SIZE) -> str:
    file_size = path.stat().st_size
    digest = hashlib.blake2b(digest_size=20)
    digest.update(file_size.to_bytes(16, byteorder="little", signed=False))

    with path.open("rb") as handle:
        for offset in _sample_offsets(file_size, sample_size):
            handle.seek(offset)
            chunk = handle.read(sample_size)
            digest.update(chunk)

    return digest.hexdigest()


def compute_full_hash(path: Path, chunk_size: int = HASH_CHUNK_SIZE) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(chunk_size)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def files_are_identical(first_path: Path, second_path: Path, chunk_size: int = HASH_CHUNK_SIZE) -> bool:
    if first_path.stat().st_size != second_path.stat().st_size:
        return False

    with first_path.open("rb") as first_handle, second_path.open("rb") as second_handle:
        while True:
            first_chunk = first_handle.read(chunk_size)
            second_chunk = second_handle.read(chunk_size)
            if first_chunk != second_chunk:
                return False
            if not first_chunk:
                return True


def _safe_file_size(path: Path) -> int | None:
    try:
        return path.stat().st_size
    except OSError:
        return None


def _record_stage_error(result: DuplicateScanResult, stage: str) -> None:
    result.errors += 1
    if stage == "size":
        result.size_group_errors += 1
    elif stage == "sample":
        result.sample_errors += 1
    elif stage == "hash":
        result.hash_errors += 1
    elif stage == "compare":
        result.compare_errors += 1
    else:  # pragma: no cover - safeguard against typos in future changes
        raise ValueError(f"Unknown duplicate scan stage: {stage}")


def _group_by_size(
    paths: list[Path],
    result: DuplicateScanResult | None = None,
) -> dict[int, list[Path]]:
    """
    Group files by size.

    Backward-compatibility note:
    Older tests and internal self-checks call this helper with only the path list.
    The `result` parameter is therefore optional even though newer scan code passes
    the active `DuplicateScanResult` to collect stage-specific error counters.
    """
    grouped: dict[int, list[Path]] = defaultdict(list)
    for path in paths:
        file_size = _safe_file_size(path)
        if file_size is None:
            if result is not None:
                _record_stage_error(result, "size")
            continue
        grouped[file_size].append(path)
    return grouped


def _group_by_date(
    paths: list[Path],
    result: DuplicateScanResult | None = None,
    progress_callback: ProgressCallback | None = None,
) -> dict[str, list[Path]]:
    date_groups: dict[str, list[Path]] = defaultdict(list)
    batch_size = 2000
    total = len(paths)
    processed = 0

    for i in range(0, total, batch_size):
        batch = paths[i:i + batch_size]
        metadata_map = read_exiftool_metadata_batch(batch, timeout_seconds=60)

        for path in batch:
            meta = metadata_map.get(path, {})
            if meta:
                date_val = (
                    meta.get("DateTimeOriginal")
                    or meta.get("CreateDate")
                    or ""
                )
                if date_val and isinstance(date_val, str):
                    date_key = str(date_val)[:10]
                    if date_key:
                        date_groups[date_key].append(path)
                        processed += 1
                        continue

            try:
                mtime = path.stat().st_mtime
                date_key = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")
            except OSError:
                date_key = "unknown"
            date_groups[date_key].append(path)
            processed += 1

        if progress_callback and processed % 2000 == 0:
            progress_callback(
                f"Date grouping: {processed}/{total} files ({processed * 100 // max(total, 1)}%)"
            )

    return {k: v for k, v in date_groups.items() if len(v) > 1}


def _build_exact_group(paths: list[Path], file_size: int, sample_digest: str, full_digest: str) -> ExactDuplicateGroup:
    ordered_paths = sorted(paths, key=_normalized_sort_key)
    first_name = ordered_paths[0].name
    first_suffix = ordered_paths[0].suffix.lower()
    return ExactDuplicateGroup(
        files=ordered_paths,
        file_size=file_size,
        sample_digest=sample_digest,
        full_digest=full_digest,
        same_name=all(path.name == first_name for path in ordered_paths),
        same_suffix=all(path.suffix.lower() == first_suffix for path in ordered_paths),
        extension_summary=_extension_summary(ordered_paths),
        media_kind_summary=_media_kind_summary(ordered_paths),
    )


def _source_root_for_path(path: Path, source_dirs: list[Path]) -> Path | None:
    for source_dir in sorted(source_dirs, key=lambda item: len(str(item)), reverse=True):
        try:
            path.relative_to(source_dir)
        except ValueError:
            continue
        return source_dir
    return None


def _apply_duplicate_path_filters(paths: list[Path], config: DuplicateScanConfig, result: DuplicateScanResult) -> list[Path]:
    if not config.include_patterns and not config.exclude_patterns:
        return paths
    filtered: list[Path] = []
    for path in paths:
        source_root = _source_root_for_path(path, config.source_dirs)
        if path_is_included_by_patterns(
            path,
            include_patterns=config.include_patterns,
            exclude_patterns=config.exclude_patterns,
            source_root=source_root,
        ):
            filtered.append(path)
        else:
            result.skipped_filtered_files += 1
    return filtered


def _dedup_filter(states: dict[Path, dict], key_fn, min_count: int = 2) -> dict:
    """Return a subset of *states* where *key_fn*(state) appears >= *min_count* times."""
    key_counts: dict[str, int] = {}
    for state in states.values():
        k = key_fn(state)
        if k is not None:
            key_counts[k] = key_counts.get(k, 0) + 1
    return {path: state for path, state in states.items()
            if key_counts.get(key_fn(state)) is not None and key_counts[key_fn(state)] >= min_count}


def _byte_compare_clusters(
    paths: list[Path],
    config: DuplicateScanConfig,
    result: DuplicateScanResult,
) -> list[list[Path]]:
    """Group *paths* whose (size, sample, hash) match into byte-identical clusters."""
    clustered: list[list[Path]] = []
    for path in paths:
        placed = False
        for cluster in clustered:
            try:
                if files_are_identical(path, cluster[0], chunk_size=config.hash_chunk_size):
                    cluster.append(path)
                    placed = True
                    break
            except OSError:
                _record_stage_error(result, "compare")
                placed = True
                break
        if not placed:
            clustered.append([path])
    return clustered


def scan_exact_duplicates(
    config: DuplicateScanConfig,
    progress_callback: ProgressCallback | None = None,
    early_group_callback: Callable[[ExactDuplicateGroup], None] | None = None,
) -> DuplicateScanResult:
    with timer("scan_exact_duplicates", _logger):
        return _scan_exact_duplicates_impl(config, progress_callback, early_group_callback=early_group_callback)


def _scan_exact_duplicates_impl(
    config: DuplicateScanConfig,
    progress_callback: ProgressCallback | None = None,
    *,
    early_group_callback: Callable[[ExactDuplicateGroup], None] | None = None,
) -> DuplicateScanResult:
    result = DuplicateScanResult()

    _emit_progress(progress_callback, "Scanning source folders for media files ...")
    media_extensions = None if config.media_extensions is None else normalize_extensions(config.media_extensions)
    media_files = _apply_duplicate_path_filters(
        iter_media_files(config.source_dirs, media_extensions=media_extensions),
        config,
        result,
    )
    result.scanned_files = len(media_files)
    _apply_scan_kind_summary(result, media_files)
    _emit_progress(
        progress_callback,
        f"Found {result.scanned_files} media file(s): images={result.image_file_count}, raw={result.raw_image_file_count}, videos={result.video_file_count}, audio={result.audio_file_count}.",
    )

    if result.scanned_files == 0:
        _emit_progress(progress_callback, "No media files found.")
        return result

    # ── Unified state tracker: path → {stage data} ──
    # Single dict avoids 4× path-list duplication across stages.
    states: dict[Path, dict] = {}

    # Stage 1/4 — size grouping
    for path in media_files:
        file_size = _safe_file_size(path)
        if file_size is None:
            _record_stage_error(result, "size")
            continue
        states[path] = {"size": file_size}

    states = _dedup_filter(states, lambda s: str(s["size"]))
    stage_size = len(states)
    result.size_candidate_groups = len({s["size"] for s in states.values()} if states else set())
    result.size_candidate_files = stage_size
    stage_one_message = (
        f"Stage 1/4 — size grouping kept {stage_size} candidate file(s) "
        f"in {result.size_candidate_groups} group(s)."
    )
    if result.size_group_errors > 0:
        stage_one_message += f" Skipped {result.size_group_errors} unreadable file(s) during size grouping."
    _emit_progress(progress_callback, stage_one_message)

    if not states:
        _emit_progress(progress_callback, "No exact duplicates found.")
        return result

    # Stage 2/4 — sample fingerprinting
    sample_count = 0
    total_samples = len(states)
    for idx, (path, state) in enumerate(tuple(states.items())):
        try:
            state["sample"] = compute_sample_fingerprint(path, sample_size=config.sample_size)
            result.sampled_files += 1
        except OSError:
            _record_stage_error(result, "sample")
            del states[path]
        sample_count += 1
        if sample_count % 500 == 0:
            _emit_progress(progress_callback, f"Stage 2/4 — sampled {sample_count}/{total_samples} files ({sample_count*100//total_samples}%)")

    states = _dedup_filter(states, lambda s: str((s["size"], s.get("sample"))))
    sample_groups = len({(s["size"], s["sample"]) for s in states.values()}) if states else 0
    _emit_progress(progress_callback, f"Stage 2/4 — sample fingerprinting complete: {len(states)} files in {sample_groups} groups")

    stage_two_message = f"Stage 2/4 — sample fingerprinting kept {len(states)} file(s)."
    if result.sample_errors > 0:
        stage_two_message += f" Sample errors: {result.sample_errors}."
    _emit_progress(progress_callback, stage_two_message)

    if not states:
        _emit_progress(progress_callback, "No exact duplicates found.")
        return result

    # Stage 3/4 — full hashing
    hash_count = 0
    total_hashes = len(states)
    for idx, (path, state) in enumerate(tuple(states.items())):
        try:
            state["hash"] = compute_full_hash(path, chunk_size=config.hash_chunk_size)
            result.hashed_files += 1
        except OSError:
            _record_stage_error(result, "hash")
            del states[path]
        hash_count += 1
        if hash_count % 500 == 0:
            _emit_progress(progress_callback, f"Stage 3/4 — hashed {hash_count}/{total_hashes} files ({hash_count*100//total_hashes}%)")

    states = _dedup_filter(states, lambda s: str((s["size"], s.get("sample"), s.get("hash"))))
    _emit_progress(progress_callback, f"Stage 3/4 — full hashing complete: {len(states)} files")

    stage_three_message = f"Stage 3/4 — full hashing kept {len(states)} file(s)."
    if result.hash_errors > 0:
        stage_three_message += f" Hash errors: {result.hash_errors}."
    _emit_progress(progress_callback, stage_three_message)

    if not states:
        _emit_progress(progress_callback, "No exact duplicates found.")
        return result

    # Stage 4/4 — byte comparison within hash groups
    # Group surviving paths by full key
    hash_groups: dict[tuple, list[Path]] = defaultdict(list)
    for path, state in states.items():
        key = (state["size"], state.get("sample"), state.get("hash"))
        hash_groups[key].append(path)

    exact_groups: list[ExactDuplicateGroup] = []
    for (file_size, sample_digest, full_digest), paths in hash_groups.items():
        for cluster in _byte_compare_clusters(paths, config, result):
            if len(cluster) > 1:
                group = _build_exact_group(cluster, file_size, sample_digest, full_digest)
                exact_groups.append(group)
                if early_group_callback is not None:
                    early_group_callback(group)

    exact_groups.sort(key=lambda group: (-len(group.files), -group.file_size, _normalized_sort_key(group.files[0])))
    result.exact_groups = exact_groups
    result.exact_duplicate_files = sum(len(group.files) for group in exact_groups)
    result.exact_duplicates = sum(len(group.files) - 1 for group in exact_groups)
    stage_four_message = f"Stage 4/4 — byte comparison confirmed {len(result.exact_groups)} exact group(s)."
    if result.compare_errors > 0:
        stage_four_message += f" Compare errors: {result.compare_errors}."
    _emit_progress(progress_callback, stage_four_message)

    if result.exact_groups:
        _emit_progress(
            progress_callback,
            f"Finished. Exact groups: {len(result.exact_groups)} | duplicate files: {result.exact_duplicate_files} | extra duplicates: {result.exact_duplicates} | errors: {result.errors}",
        )
    else:
        _emit_progress(progress_callback, f"No exact duplicates found. Errors: {result.errors}")
    return result


def scan_exact_duplicates_fast(
    config: DuplicateScanConfig,
    progress_callback: ProgressCallback | None = None,
    early_group_callback: Callable[[ExactDuplicateGroup], None] | None = None,
) -> DuplicateScanResult:
    with timer("scan_exact_duplicates_fast", _logger):
        return _scan_exact_duplicates_fast_impl(config, progress_callback, early_group_callback=early_group_callback)


def _scan_exact_duplicates_fast_impl(
    config: DuplicateScanConfig,
    progress_callback: ProgressCallback | None = None,
    *,
    early_group_callback: Callable[[ExactDuplicateGroup], None] | None = None,
) -> DuplicateScanResult:
    result = DuplicateScanResult()

    _emit_progress(progress_callback, "Scanning source folders for media files ...")
    media_extensions = None if config.media_extensions is None else normalize_extensions(config.media_extensions)
    media_files = _apply_duplicate_path_filters(
        iter_media_files(config.source_dirs, media_extensions=media_extensions),
        config,
        result,
    )
    result.scanned_files = len(media_files)
    _apply_scan_kind_summary(result, media_files)
    _emit_progress(
        progress_callback,
        f"Found {result.scanned_files} media file(s): images={result.image_file_count}, raw={result.raw_image_file_count}, videos={result.video_file_count}, audio={result.audio_file_count}.",
    )

    if result.scanned_files == 0:
        _emit_progress(progress_callback, "No media files found.")
        return result

    # Stage 1/3 — Size-grouping
    _emit_progress(progress_callback, f"Stage 1/3 — Size grouping ({result.scanned_files} files)...")
    size_groups = _group_by_size(media_files, result)
    candidates: dict[int, list[Path]] = {size: paths for size, paths in size_groups.items() if len(paths) > 1}

    result.size_candidate_groups = len(candidates)
    result.size_candidate_files = sum(len(v) for v in candidates.values())
    _emit_progress(
        progress_callback,
        f"Stage 1/3 — size grouping kept {result.size_candidate_files} candidate file(s) in {result.size_candidate_groups} group(s).",
    )

    if not candidates:
        _emit_progress(progress_callback, "No exact duplicates found.")
        return result

    # Stage 2/3 — Date-group each size group
    _emit_progress(progress_callback, f"Stage 2/3 — Date grouping within {len(candidates)} size groups...")
    final_candidates: dict[str, list[Path]] = {}
    candidate_count = 0
    processed_groups = 0
    total_size_groups = len(candidates)

    for size, paths in candidates.items():
        processed_groups += 1
        date_groups = _group_by_date(paths, result)
        for date_key, date_paths in date_groups.items():
            if len(date_paths) > 1:
                key = f"{size}:{date_key}"
                final_candidates[key] = date_paths
                candidate_count += len(date_paths)

        if progress_callback and processed_groups % 50 == 0:
            progress_callback(
                f"Stage 2/3 — Processed {processed_groups}/{total_size_groups} size groups, {candidate_count} candidates so far"
            )

    _emit_progress(
        progress_callback,
        f"Stage 2/3 complete — {candidate_count} candidate files in {len(final_candidates)} date+size groups",
    )

    if not final_candidates:
        _emit_progress(progress_callback, "No exact duplicates found.")
        return result

    # Stage 3/3 — Sample fingerprint + hash + byte-compare on date-filtered candidates
    _emit_progress(progress_callback, f"Stage 3/3 — Sample fingerprint on {candidate_count} candidates...")

    states: dict[Path, dict] = {}
    for paths in final_candidates.values():
        for path in paths:
            file_size = _safe_file_size(path)
            if file_size is None:
                _record_stage_error(result, "size")
                continue
            states[path] = {"size": file_size}

    sample_count = 0
    total_samples = len(states)
    for idx, (path, state) in enumerate(tuple(states.items())):
        try:
            state["sample"] = compute_sample_fingerprint(path, sample_size=config.sample_size)
            result.sampled_files += 1
        except OSError:
            _record_stage_error(result, "sample")
            del states[path]
        sample_count += 1
        if sample_count % 500 == 0:
            pct = sample_count * 100 // max(total_samples, 1)
            _emit_progress(progress_callback, f"Stage 3/3 — sampled {sample_count}/{total_samples} files ({pct}%)")

    states = _dedup_filter(states, lambda s: str((s["size"], s.get("sample"))))
    sample_groups = len({(s["size"], s["sample"]) for s in states.values()}) if states else 0
    _emit_progress(progress_callback, f"Stage 3/3 — sample fingerprinting kept {len(states)} files in {sample_groups} groups")

    if not states:
        _emit_progress(progress_callback, "No exact duplicates found.")
        return result

    hash_count = 0
    total_hashes = len(states)
    for idx, (path, state) in enumerate(tuple(states.items())):
        try:
            state["hash"] = compute_full_hash(path, chunk_size=config.hash_chunk_size)
            result.hashed_files += 1
        except OSError:
            _record_stage_error(result, "hash")
            del states[path]
        hash_count += 1
        if hash_count % 500 == 0:
            pct = hash_count * 100 // max(total_hashes, 1)
            _emit_progress(progress_callback, f"Stage 3/3 — hashed {hash_count}/{total_hashes} files ({pct}%)")

    states = _dedup_filter(states, lambda s: str((s["size"], s.get("sample"), s.get("hash"))))
    _emit_progress(progress_callback, f"Stage 3/3 — full hashing kept {len(states)} files")

    if not states:
        _emit_progress(progress_callback, "No exact duplicates found.")
        return result

    hash_groups: dict[tuple, list[Path]] = defaultdict(list)
    for path, state in states.items():
        key = (state["size"], state.get("sample"), state.get("hash"))
        hash_groups[key].append(path)

    exact_groups: list[ExactDuplicateGroup] = []
    for (file_size, sample_digest, full_digest), paths in hash_groups.items():
        for cluster in _byte_compare_clusters(paths, config, result):
            if len(cluster) > 1:
                group = _build_exact_group(cluster, file_size, sample_digest, full_digest)
                exact_groups.append(group)
                if early_group_callback is not None:
                    early_group_callback(group)

    exact_groups.sort(key=lambda group: (-len(group.files), -group.file_size, _normalized_sort_key(group.files[0])))
    result.exact_groups = exact_groups
    result.exact_duplicate_files = sum(len(group.files) for group in exact_groups)
    result.exact_duplicates = sum(len(group.files) - 1 for group in exact_groups)

    stage_message = f"Stage 3/3 — byte comparison confirmed {len(result.exact_groups)} exact group(s)."
    if result.compare_errors > 0:
        stage_message += f" Compare errors: {result.compare_errors}."
    _emit_progress(progress_callback, stage_message)

    if result.exact_groups:
        _emit_progress(
            progress_callback,
            f"Finished. Exact groups: {len(result.exact_groups)} | duplicate files: {result.exact_duplicate_files} | extra duplicates: {result.exact_duplicates} | errors: {result.errors}",
        )
    else:
        _emit_progress(progress_callback, f"No exact duplicates found. Errors: {result.errors}")
    return result
