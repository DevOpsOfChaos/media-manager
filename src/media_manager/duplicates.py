from __future__ import annotations

import hashlib
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

from .sorter import iter_media_files

ProgressCallback = Callable[[str], None]


@dataclass(slots=True)
class DuplicateScanConfig:
    source_dirs: list[Path]
    sample_size: int = 64 * 1024
    hash_chunk_size: int = 1024 * 1024


@dataclass(slots=True)
class ExactDuplicateGroup:
    files: list[Path]
    file_size: int
    sample_digest: str
    full_digest: str
    same_name: bool
    same_suffix: bool


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


def _emit_progress(progress_callback: ProgressCallback | None, message: str) -> None:
    if progress_callback is not None:
        progress_callback(message)


def _normalized_sort_key(path: Path) -> str:
    return str(path).lower()


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


def compute_sample_fingerprint(path: Path, sample_size: int = 64 * 1024) -> str:
    file_size = path.stat().st_size
    digest = hashlib.blake2b(digest_size=20)
    digest.update(file_size.to_bytes(16, byteorder="little", signed=False))

    with path.open("rb") as handle:
        for offset in _sample_offsets(file_size, sample_size):
            handle.seek(offset)
            chunk = handle.read(sample_size)
            digest.update(chunk)

    return digest.hexdigest()


def compute_full_hash(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(chunk_size)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def files_are_identical(first_path: Path, second_path: Path, chunk_size: int = 1024 * 1024) -> bool:
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
    )


def scan_exact_duplicates(
    config: DuplicateScanConfig,
    progress_callback: ProgressCallback | None = None,
) -> DuplicateScanResult:
    result = DuplicateScanResult()

    _emit_progress(progress_callback, "Scanning source folders for media files ...")
    media_files = iter_media_files(config.source_dirs)
    result.scanned_files = len(media_files)
    _emit_progress(progress_callback, f"Found {result.scanned_files} media file(s).")

    if result.scanned_files == 0:
        _emit_progress(progress_callback, "No media files found.")
        return result

    size_groups = _group_by_size(media_files, result)
    candidate_size_groups = {
        size: sorted(paths, key=_normalized_sort_key)
        for size, paths in size_groups.items()
        if len(paths) > 1
    }
    result.size_candidate_groups = len(candidate_size_groups)
    result.size_candidate_files = sum(len(paths) for paths in candidate_size_groups.values())
    stage_one_message = (
        f"Stage 1/4 — size grouping kept {result.size_candidate_files} candidate file(s) "
        f"in {result.size_candidate_groups} group(s)."
    )
    if result.size_group_errors > 0:
        stage_one_message += f" Skipped {result.size_group_errors} unreadable file(s) during size grouping."
    _emit_progress(progress_callback, stage_one_message)

    if result.size_candidate_files == 0:
        _emit_progress(progress_callback, "No exact duplicates found.")
        return result

    sampled_groups: dict[tuple[int, str], list[Path]] = defaultdict(list)
    for file_size, paths in candidate_size_groups.items():
        for path in paths:
            try:
                sample_digest = compute_sample_fingerprint(path, sample_size=config.sample_size)
            except OSError:
                _record_stage_error(result, "sample")
                continue
            result.sampled_files += 1
            sampled_groups[(file_size, sample_digest)].append(path)

    sample_candidates = {
        key: sorted(paths, key=_normalized_sort_key)
        for key, paths in sampled_groups.items()
        if len(paths) > 1
    }
    stage_two_message = f"Stage 2/4 — sample fingerprinting kept {sum(len(paths) for paths in sample_candidates.values())} file(s)."
    if result.sample_errors > 0:
        stage_two_message += f" Sample errors: {result.sample_errors}."
    _emit_progress(progress_callback, stage_two_message)

    if not sample_candidates:
        _emit_progress(progress_callback, "No exact duplicates found.")
        return result

    hashed_groups: dict[tuple[int, str, str], list[Path]] = defaultdict(list)
    for (file_size, sample_digest), paths in sample_candidates.items():
        for path in paths:
            try:
                full_digest = compute_full_hash(path, chunk_size=config.hash_chunk_size)
            except OSError:
                _record_stage_error(result, "hash")
                continue
            result.hashed_files += 1
            hashed_groups[(file_size, sample_digest, full_digest)].append(path)

    full_hash_candidates = {
        key: sorted(paths, key=_normalized_sort_key)
        for key, paths in hashed_groups.items()
        if len(paths) > 1
    }
    stage_three_message = f"Stage 3/4 — full hashing kept {sum(len(paths) for paths in full_hash_candidates.values())} file(s)."
    if result.hash_errors > 0:
        stage_three_message += f" Hash errors: {result.hash_errors}."
    _emit_progress(progress_callback, stage_three_message)

    if not full_hash_candidates:
        _emit_progress(progress_callback, "No exact duplicates found.")
        return result

    exact_groups: list[ExactDuplicateGroup] = []
    for (file_size, sample_digest, full_digest), paths in full_hash_candidates.items():
        clustered_paths: list[list[Path]] = []
        for path in paths:
            placed = False
            for cluster in clustered_paths:
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
                clustered_paths.append([path])

        for cluster in clustered_paths:
            if len(cluster) > 1:
                exact_groups.append(_build_exact_group(cluster, file_size, sample_digest, full_digest))

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
