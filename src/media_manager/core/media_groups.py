from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
import hashlib
import os
from pathlib import Path
from typing import Iterable

from media_manager.core.scanner.models import ScannedFile

SIDECARExt = frozenset({".xmp", ".aae"})
RAW_EXTENSIONS = frozenset({".dng", ".raw", ".arw", ".cr2", ".cr3", ".nef", ".orf", ".rw2"})
JPEG_EXTENSIONS = frozenset({".jpg", ".jpeg", ".jpe", ".jfif"})
PHOTO_VIDEO_IMAGE_EXTENSIONS = frozenset({".jpg", ".jpeg", ".jpe", ".jfif", ".heic", ".heif"})
PHOTO_VIDEO_VIDEO_EXTENSIONS = frozenset({".mov", ".mp4"})


@dataclass(slots=True, frozen=True)
class MediaAssociationWarning:
    path: Path
    warning_code: str
    message: str


@dataclass(slots=True, frozen=True)
class MediaGroupMember:
    path: Path
    role: str
    extension: str


@dataclass(slots=True, frozen=True)
class MediaGroup:
    group_id: str
    source_root: Path
    main_path: Path
    group_kind: str
    members: tuple[MediaGroupMember, ...]
    association_warnings: tuple[MediaAssociationWarning, ...] = ()

    @property
    def associated_paths(self) -> tuple[Path, ...]:
        return tuple(item.path for item in self.members if item.role != "main")

    @property
    def total_file_count(self) -> int:
        return len(self.members)

    @property
    def associated_file_count(self) -> int:
        return len(self.associated_paths)


@dataclass(slots=True, frozen=True)
class MediaGroupSummary:
    group_count: int
    single_file_count: int
    associated_file_count: int
    association_warning_count: int
    group_kind_summary: dict[str, int]


def _normalized_extension(path: Path) -> str:
    return path.suffix.lower()


def _normalized_sort_key(path: Path) -> tuple[str, str]:
    return (os.path.normcase(str(path.parent)), os.path.normcase(path.name))


def _bucket_key(item: ScannedFile) -> tuple[str, str, str]:
    relative_parent = item.relative_path.parent.as_posix().casefold() if item.relative_path.parent != Path(".") else ""
    return (
        os.path.normcase(str(item.source_root)),
        relative_parent,
        item.path.stem.casefold(),
    )


def _build_group_id(source_root: Path, main_path: Path) -> str:
    seed = f"{os.path.normcase(str(source_root))}|{os.path.normcase(str(main_path))}"
    digest = hashlib.sha1(seed.encode("utf-8")).hexdigest()[:12]
    return f"media-group-{digest}"


def _build_warning(files: list[ScannedFile], warning_code: str, message: str) -> tuple[MediaAssociationWarning, ...]:
    return tuple(
        MediaAssociationWarning(path=item.path, warning_code=warning_code, message=message)
        for item in sorted(files, key=lambda entry: _normalized_sort_key(entry.path))
    )


def _role_for_associated(path: Path) -> str:
    extension = _normalized_extension(path)
    if extension == ".xmp":
        return "sidecar_xmp"
    if extension == ".aae":
        return "sidecar_aae"
    if extension in RAW_EXTENSIONS:
        return "raw_sibling"
    if extension in JPEG_EXTENSIONS:
        return "jpeg_sibling"
    if extension in PHOTO_VIDEO_VIDEO_EXTENSIONS:
        return "paired_video"
    return "associated"


def _build_group(
    *,
    main_file: ScannedFile,
    associated_files: list[ScannedFile],
    group_kind: str,
    warnings: tuple[MediaAssociationWarning, ...] = (),
) -> MediaGroup:
    members = [
        MediaGroupMember(path=main_file.path, role="main", extension=_normalized_extension(main_file.path))
    ]
    for item in sorted(associated_files, key=lambda entry: _normalized_sort_key(entry.path)):
        members.append(
            MediaGroupMember(path=item.path, role=_role_for_associated(item.path), extension=_normalized_extension(item.path))
        )
    return MediaGroup(
        group_id=_build_group_id(main_file.source_root, main_file.path),
        source_root=main_file.source_root,
        main_path=main_file.path,
        group_kind=group_kind,
        members=tuple(members),
        association_warnings=warnings,
    )


def _build_single_group(item: ScannedFile, warnings: tuple[MediaAssociationWarning, ...] = ()) -> MediaGroup:
    return MediaGroup(
        group_id=_build_group_id(item.source_root, item.path),
        source_root=item.source_root,
        main_path=item.path,
        group_kind="single",
        members=(MediaGroupMember(path=item.path, role="main", extension=_normalized_extension(item.path)),),
        association_warnings=warnings,
    )


def _build_groups_for_bucket(files_in_bucket: list[ScannedFile]) -> list[MediaGroup]:
    files_in_bucket = sorted(files_in_bucket, key=lambda item: _normalized_sort_key(item.path))
    sidecars = [item for item in files_in_bucket if _normalized_extension(item.path) in SIDECARExt]
    raws = [item for item in files_in_bucket if _normalized_extension(item.path) in RAW_EXTENSIONS]
    jpegs = [item for item in files_in_bucket if _normalized_extension(item.path) in JPEG_EXTENSIONS]
    image_video_images = [item for item in files_in_bucket if _normalized_extension(item.path) in PHOTO_VIDEO_IMAGE_EXTENSIONS]
    image_video_videos = [item for item in files_in_bucket if _normalized_extension(item.path) in PHOTO_VIDEO_VIDEO_EXTENSIONS]
    media_files = [item for item in files_in_bucket if _normalized_extension(item.path) not in SIDECARExt]

    if len(files_in_bucket) == 1:
        return [_build_single_group(files_in_bucket[0])]

    if len(raws) > 1:
        warnings = _build_warning(raws, "ambiguous_raw_jpeg_pair", "multiple RAW candidates share the same stem")
        return [_build_single_group(item, warnings) for item in files_in_bucket]

    if len(jpegs) > 1 and len(raws) >= 1:
        warnings = _build_warning(jpegs, "ambiguous_raw_jpeg_pair", "multiple JPEG candidates share the same stem")
        return [_build_single_group(item, warnings) for item in files_in_bucket]

    if len(image_video_images) > 1 and len(image_video_videos) >= 1:
        warnings = _build_warning(
            image_video_images,
            "ambiguous_photo_video_pair",
            "multiple image candidates share the same stem for photo/video pairing",
        )
        return [_build_single_group(item, warnings) for item in files_in_bucket]

    if len(image_video_videos) > 1 and len(image_video_images) >= 1:
        warnings = _build_warning(
            image_video_videos,
            "ambiguous_photo_video_pair",
            "multiple video candidates share the same stem for photo/video pairing",
        )
        return [_build_single_group(item, warnings) for item in files_in_bucket]

    if len(media_files) == 1 and sidecars:
        return [_build_group(main_file=media_files[0], associated_files=sidecars, group_kind="sidecar")]

    if len(raws) == 1 and len(jpegs) == 1:
        raw_file = raws[0]
        jpeg_file = jpegs[0]
        non_pair_media = [
            item.path
            for item in media_files
            if item.path not in {raw_file.path, jpeg_file.path}
        ]
        if not non_pair_media:
            kind = "raw_jpeg_pair" if not sidecars else "mixed"
            associated = [jpeg_file, *sidecars]
            return [_build_group(main_file=raw_file, associated_files=associated, group_kind=kind)]

    if len(image_video_images) == 1 and len(image_video_videos) == 1:
        image_file = image_video_images[0]
        video_file = image_video_videos[0]
        non_pair_media = [
            item.path
            for item in media_files
            if item.path not in {image_file.path, video_file.path}
        ]
        if not non_pair_media:
            kind = "photo_video_pair" if not sidecars else "mixed"
            associated = [video_file, *sidecars]
            return [_build_group(main_file=image_file, associated_files=associated, group_kind=kind)]

    warnings = _build_warning(
        files_in_bucket,
        "unsupported_association",
        "files share the same stem but do not match a safe supported association rule",
    )
    return [_build_single_group(item, warnings) for item in files_in_bucket]


def build_media_groups(files: Iterable[ScannedFile]) -> list[MediaGroup]:
    buckets: dict[tuple[str, str, str], list[ScannedFile]] = defaultdict(list)
    for item in files:
        buckets[_bucket_key(item)].append(item)

    groups: list[MediaGroup] = []
    for _, bucket_files in sorted(buckets.items(), key=lambda item: item[0]):
        groups.extend(_build_groups_for_bucket(bucket_files))

    groups.sort(key=lambda item: (os.path.normcase(str(item.source_root)), os.path.normcase(str(item.main_path))))
    return groups


def summarize_media_groups(groups: Iterable[MediaGroup]) -> MediaGroupSummary:
    group_list = list(groups)
    kind_counter = Counter(item.group_kind for item in group_list)
    return MediaGroupSummary(
        group_count=len(group_list),
        single_file_count=sum(1 for item in group_list if item.group_kind == "single"),
        associated_file_count=sum(item.associated_file_count for item in group_list),
        association_warning_count=sum(len(item.association_warnings) for item in group_list),
        group_kind_summary=dict(sorted(kind_counter.items())),
    )


def find_group_for_path(groups: Iterable[MediaGroup], path: Path) -> MediaGroup | None:
    group_index = build_media_group_index(groups)
    return group_index.get(path)


def build_media_group_index(groups: Iterable[MediaGroup]) -> dict[Path, MediaGroup]:
    index: dict[Path, MediaGroup] = {}
    for group in groups:
        for member in group.members:
            index[member.path] = group
    return index


__all__ = [
    "MediaAssociationWarning",
    "MediaGroupMember",
    "MediaGroup",
    "MediaGroupSummary",
    "build_media_groups",
    "summarize_media_groups",
    "find_group_for_path",
    "build_media_group_index",
]
