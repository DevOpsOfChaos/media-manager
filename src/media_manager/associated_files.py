from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

PRIMARY_MEDIA_SUFFIXES = {
    ".jpg",
    ".jpeg",
    ".png",
    ".heic",
    ".heif",
    ".cr2",
    ".cr3",
    ".nef",
    ".arw",
    ".orf",
    ".raf",
    ".rw2",
    ".dng",
    ".mp4",
    ".mov",
    ".mkv",
    ".avi",
    ".mts",
    ".m2ts",
}

SIDECAR_SUFFIXES = {
    ".xmp",
    ".aae",
    ".srt",
    ".thm",
    ".lrv",
    ".wav",
}


@dataclass(slots=True)
class AssociatedFileGroup:
    key: str
    primaries: list[Path] = field(default_factory=list)
    sidecars: list[Path] = field(default_factory=list)
    others: list[Path] = field(default_factory=list)

    @property
    def all_files(self) -> list[Path]:
        return [*self.primaries, *self.sidecars, *self.others]

    @property
    def has_relationship(self) -> bool:
        return len(self.all_files) > 1 and bool(self.primaries)



def associated_key_for_path(path: str | Path) -> str:
    file_path = Path(path)
    return file_path.stem.casefold()



def classify_associated_path(path: str | Path) -> str:
    suffix = Path(path).suffix.casefold()
    if suffix in PRIMARY_MEDIA_SUFFIXES:
        return "primary"
    if suffix in SIDECAR_SUFFIXES:
        return "sidecar"
    return "other"



def group_associated_files(paths: list[str | Path]) -> list[AssociatedFileGroup]:
    buckets: dict[str, AssociatedFileGroup] = {}

    for raw_path in paths:
        path = Path(raw_path)
        key = associated_key_for_path(path)
        group = buckets.setdefault(key, AssociatedFileGroup(key=key))
        category = classify_associated_path(path)

        if category == "primary":
            group.primaries.append(path)
        elif category == "sidecar":
            group.sidecars.append(path)
        else:
            group.others.append(path)

    result = [group for group in buckets.values() if group.has_relationship]
    result.sort(key=lambda group: group.key)

    for group in result:
        group.primaries.sort(key=lambda path: str(path).casefold())
        group.sidecars.sort(key=lambda path: str(path).casefold())
        group.others.sort(key=lambda path: str(path).casefold())

    return result



def build_associated_file_map(paths: list[str | Path]) -> dict[str, list[str]]:
    relation_map: dict[str, list[str]] = {}

    for group in group_associated_files(paths):
        related = [str(path) for path in group.all_files]
        for path in group.all_files:
            relation_map[str(path)] = [candidate for candidate in related if candidate != str(path)]

    return relation_map
