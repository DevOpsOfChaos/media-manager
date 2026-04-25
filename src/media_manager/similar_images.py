from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

from .core.path_filters import path_is_included_by_patterns
from .media_formats import list_supported_media_extensions, list_supported_similar_image_extensions, normalize_extensions
from .sorter import iter_media_files

try:  # pragma: no cover - optional dependency guard
    from PIL import Image
except Exception:  # pragma: no cover - runtime fallback
    Image = None

ProgressCallback = Callable[[str], None]
IMAGE_EXTENSIONS = list_supported_similar_image_extensions()


@dataclass(slots=True, frozen=True)
class SimilarImageScanConfig:
    source_dirs: list[Path]
    hash_size: int = 8
    max_distance: int = 6
    include_patterns: tuple[str, ...] = ()
    exclude_patterns: tuple[str, ...] = ()
    media_extensions: frozenset[str] | None = None


@dataclass(slots=True, frozen=True)
class SimilarImageMember:
    path: Path
    hash_hex: str
    distance: int
    width: int | None = None
    height: int | None = None


@dataclass(slots=True)
class SimilarImageGroup:
    anchor_path: Path
    members: list[SimilarImageMember] = field(default_factory=list)


@dataclass(slots=True)
class SimilarImageScanResult:
    scanned_files: int = 0
    image_files: int = 0
    hashed_files: int = 0
    candidate_pairs_checked: int = 0
    exact_hash_pairs: int = 0
    similar_pairs: int = 0
    similar_groups: list[SimilarImageGroup] = field(default_factory=list)
    errors: int = 0
    decode_errors: int = 0
    skipped_filtered_files: int = 0


def _emit_progress(progress_callback: ProgressCallback | None, message: str) -> None:
    if progress_callback is not None:
        progress_callback(message)


def _normalized_sort_key(path: Path) -> str:
    return str(path).lower()


def _source_root_for_path(path: Path, source_dirs: list[Path]) -> Path | None:
    for source_dir in sorted(source_dirs, key=lambda item: len(str(item)), reverse=True):
        try:
            path.relative_to(source_dir)
        except ValueError:
            continue
        return source_dir
    return None


def _ensure_pillow() -> None:
    if Image is None:
        raise RuntimeError("Pillow is required for similar image scanning. Install the project dependencies again.")


def compute_average_hash_details(path: Path, hash_size: int = 8) -> tuple[int, tuple[int, int]]:
    _ensure_pillow()
    if hash_size <= 0:
        raise ValueError("hash_size must be greater than zero")

    with Image.open(path) as handle:
        source_width, source_height = handle.size
        image = handle.convert("L").resize((hash_size, hash_size), Image.Resampling.LANCZOS)
    flattened = getattr(image, "get_flattened_data", None)
    pixels = list(flattened() if callable(flattened) else image.getdata())
    average = sum(pixels) / len(pixels)

    value = 0
    for pixel in pixels:
        value = (value << 1) | int(pixel >= average)
    return value, (source_width, source_height)


def compute_average_hash(path: Path, hash_size: int = 8) -> int:
    return compute_average_hash_details(path, hash_size=hash_size)[0]


def hash_to_hex(hash_value: int, hash_size: int) -> str:
    width = max(1, (hash_size * hash_size + 3) // 4)
    return f"{hash_value:0{width}x}"


def hamming_distance(first_hash: int, second_hash: int) -> int:
    return (first_hash ^ second_hash).bit_count()


def scan_similar_images(
    config: SimilarImageScanConfig,
    progress_callback: ProgressCallback | None = None,
) -> SimilarImageScanResult:
    if config.max_distance < 0:
        raise ValueError("max_distance must be zero or greater")

    if config.hash_size <= 0:
        raise ValueError("hash_size must be greater than zero")

    result = SimilarImageScanResult()
    scan_extensions = list_supported_media_extensions()
    if config.media_extensions is not None:
        scan_extensions = normalize_extensions(config.media_extensions) & scan_extensions
    media_files = iter_media_files(config.source_dirs, media_extensions=scan_extensions)
    result.scanned_files = len(media_files)

    similar_extensions = set(IMAGE_EXTENSIONS)
    if config.media_extensions is not None:
        similar_extensions &= normalize_extensions(config.media_extensions)

    image_files: list[Path] = []
    for path in media_files:
        if path.suffix.lower() not in similar_extensions:
            continue
        if path_is_included_by_patterns(
            path,
            include_patterns=config.include_patterns,
            exclude_patterns=config.exclude_patterns,
            source_root=_source_root_for_path(path, config.source_dirs),
        ):
            image_files.append(path)
        else:
            result.skipped_filtered_files += 1

    result.image_files = len(image_files)
    _emit_progress(
        progress_callback,
        f"Found {result.image_files} similarity-capable image file(s) among {result.scanned_files} media file(s).",
    )

    if result.image_files == 0:
        return result

    hashes: dict[Path, int] = {}
    dimensions: dict[Path, tuple[int, int]] = {}
    for path in image_files:
        try:
            hash_value, image_size = compute_average_hash_details(path, hash_size=config.hash_size)
            hashes[path] = hash_value
            dimensions[path] = image_size
            result.hashed_files += 1
        except Exception:
            result.errors += 1
            result.decode_errors += 1

    if len(hashes) < 2:
        return result

    ordered_paths = sorted(hashes.keys(), key=_normalized_sort_key)
    adjacency: dict[Path, set[Path]] = defaultdict(set)

    for index, first_path in enumerate(ordered_paths):
        for second_path in ordered_paths[index + 1 :]:
            result.candidate_pairs_checked += 1
            distance = hamming_distance(hashes[first_path], hashes[second_path])
            if distance == 0:
                result.exact_hash_pairs += 1
            if distance <= config.max_distance:
                adjacency[first_path].add(second_path)
                adjacency[second_path].add(first_path)
                result.similar_pairs += 1

    visited: set[Path] = set()
    groups: list[SimilarImageGroup] = []
    for path in ordered_paths:
        if path in visited or path not in adjacency:
            continue
        stack = [path]
        component: list[Path] = []
        while stack:
            current = stack.pop()
            if current in visited:
                continue
            visited.add(current)
            component.append(current)
            stack.extend(sorted(adjacency[current], key=_normalized_sort_key, reverse=True))

        if len(component) < 2:
            continue
        component.sort(key=_normalized_sort_key)
        anchor_path = component[0]
        anchor_hash = hashes[anchor_path]
        groups.append(
            SimilarImageGroup(
                anchor_path=anchor_path,
                members=[
                    SimilarImageMember(
                        path=item,
                        hash_hex=hash_to_hex(hashes[item], config.hash_size),
                        distance=hamming_distance(anchor_hash, hashes[item]),
                        width=dimensions[item][0],
                        height=dimensions[item][1],
                    )
                    for item in component
                ],
            )
        )

    groups.sort(key=lambda group: (-len(group.members), _normalized_sort_key(group.anchor_path)))
    result.similar_groups = groups
    return result
