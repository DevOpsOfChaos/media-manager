from __future__ import annotations

import hashlib
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from media_manager.core.scanner.models import ScannedFile

SIDECAR_EXTENSIONS = {".xmp", ".aae"}
RAW_EXTENSIONS = {".dng", ".raw", ".arw", ".cr2", ".cr3", ".nef", ".orf", ".rw2"}
JPEG_EXTENSIONS = {".jpg", ".jpeg", ".jpe", ".jfif"}
PHOTO_VIDEO_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".jpe", ".jfif", ".heic", ".heif"}
PHOTO_VIDEO_VIDEO_EXTENSIONS = {".mov", ".mp4"}


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


def _normalize_extension(path: Path) -> str:
    return path.suffix.lower()


def _is_raw_extension(ext: str) -> bool:
    return ext in RAW_EXTENSIONS


def _is_jpeg_extension(ext: str) -> bool:
    return ext in JPEG_EXTENSIONS


def _is_photo_video_image_extension(ext: str) -> bool:
    return ext in PHOTO_VIDEO_IMAGE_EXTENSIONS


def _is_photo_video_video_extension(ext: str) -> bool:
    return ext in PHOTO_VIDEO_VIDEO_EXTENSIONS


def _stable_file_sort_key(item: ScannedFile) -> tuple[str, str, str]:
    return (
        str(item.source_root).lower(),
        item.relative_path.parent.as_posix().lower(),
        item.path.name.lower(),
    )


def _group_bucket_key(item: ScannedFile) -> tuple[str, str, str]:
    return (
        str(item.source_root).lower(),
        item.relative_path.parent.as_posix().lower(),
        item.path.stem.lower(),
    )


def _build_group_id(source_root: Path, main_path: Path) -> str:
    payload = f"{str(source_root).lower()}|{str(main_path).lower()}".encode("utf-8")
    return hashlib.sha1(payload).hexdigest()[:16]


def _member(file: ScannedFile, role: str) -> MediaGroupMember:
    return MediaGroupMember(path=file.path, role=role, extension=_normalize_extension(file.path))


def _warning(path: Path, code: str, message: str) -> MediaAssociationWarning:
    return MediaAssociationWarning(path=path, warning_code=code, message=message)


def _make_group(
    *,
    main_file: ScannedFile,
    kind: str,
    associated: list[MediaGroupMember] | None = None,
    warnings: list[MediaAssociationWarning] | None = None,
) -> MediaGroup:
    associated = associated or []
    warnings = warnings or []
    members = (_member(main_file, "main"), *associated)
    return MediaGroup(
        group_id=_build_group_id(main_file.source_root, main_file.path),
        source_root=main_file.source_root,
        main_path=main_file.path,
        group_kind=kind,
        members=tuple(members),
        association_warnings=tuple(warnings),
    )


def build_media_group_index(groups: Iterable[MediaGroup]) -> dict[Path, MediaGroup]:
    index: dict[Path, MediaGroup] = {}
    for group in groups:
        for member in group.members:
            index[member.path] = group
    return index


def find_group_for_path(groups: Iterable[MediaGroup], path: Path) -> MediaGroup | None:
    return build_media_group_index(groups).get(path)


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


def build_media_groups(files: Iterable[ScannedFile]) -> list[MediaGroup]:
    file_list = sorted(files, key=_stable_file_sort_key)
    buckets: dict[tuple[str, str, str], list[ScannedFile]] = defaultdict(list)
    for item in file_list:
        buckets[_group_bucket_key(item)].append(item)

    groups: list[MediaGroup] = []

    for _, bucket in sorted(buckets.items(), key=lambda kv: kv[0]):
        bucket = sorted(bucket, key=_stable_file_sort_key)
        raws = [item for item in bucket if _is_raw_extension(item.extension)]
        jpegs = [item for item in bucket if _is_jpeg_extension(item.extension)]
        images = [item for item in bucket if _is_photo_video_image_extension(item.extension)]
        videos = [item for item in bucket if _is_photo_video_video_extension(item.extension)]
        xmps = [item for item in bucket if item.extension.lower() == ".xmp"]
        aaes = [item for item in bucket if item.extension.lower() == ".aae"]

        consumed: set[Path] = set()
        primary_warnings: list[MediaAssociationWarning] = []
        associated_members: list[MediaGroupMember] = []
        ambiguous_paths: set[Path] = set()

        if len(raws) > 1:
            for item in raws:
                ambiguous_paths.add(item.path)
                primary_warnings.append(_warning(item.path, "ambiguous_raw_jpeg_pair", "Multiple RAW candidates found for the same stem."))
        if len(videos) > 1:
            for item in videos:
                ambiguous_paths.add(item.path)
                primary_warnings.append(_warning(item.path, "ambiguous_photo_video_pair", "Multiple video candidates found for the same stem."))

        main_file: ScannedFile | None = None
        kind = "single"

        if len(raws) == 1:
            main_file = raws[0]
            if len(jpegs) == 1:
                kind = "raw_jpeg_pair"
                associated_members.append(_member(jpegs[0], "jpeg_sibling"))
                consumed.add(jpegs[0].path)
        else:
            image_candidates = [item for item in images if item.path not in {raw.path for raw in raws}]
            if len(image_candidates) == 1:
                main_file = image_candidates[0]
                if len(videos) == 1:
                    kind = "photo_video_pair"
                    associated_members.append(_member(videos[0], "paired_video"))
                    consumed.add(videos[0].path)

        if main_file is not None:
            consumed.add(main_file.path)
            if len(xmps) == 1 and xmps[0].path not in consumed:
                associated_members.append(_member(xmps[0], "sidecar_xmp"))
                consumed.add(xmps[0].path)
                kind = "sidecar" if kind == "single" else "mixed"
            if len(aaes) == 1 and aaes[0].path not in consumed:
                associated_members.append(_member(aaes[0], "sidecar_aae"))
                consumed.add(aaes[0].path)
                kind = "sidecar" if kind == "single" else "mixed"

            groups.append(
                _make_group(
                    main_file=main_file,
                    kind=kind,
                    associated=associated_members,
                    warnings=primary_warnings,
                )
            )

        for item in bucket:
            if item.path in consumed:
                continue
            extra_warnings: list[MediaAssociationWarning] = []
            if item.path in ambiguous_paths:
                extra_warnings.append(
                    _warning(item.path, "unsupported_association", "File was left ungrouped because the association was ambiguous.")
                )
            groups.append(_make_group(main_file=item, kind="single", warnings=extra_warnings))

    groups.sort(key=lambda item: (str(item.source_root).lower(), str(item.main_path.parent).lower(), item.main_path.name.lower()))
    return groups


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
