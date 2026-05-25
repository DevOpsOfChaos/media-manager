"""Library browser bridge for the Tauri desktop app."""

from __future__ import annotations

import argparse as _ap
import datetime as _dt
import json
import os
import sys
from pathlib import Path


PHOTO_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp", ".tiff", ".tif", ".heic", ".heif"}
VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv", ".webm", ".mts", ".m2ts", ".3gp"}
RAW_EXTENSIONS = {".cr2", ".cr3", ".nef", ".arw", ".dng", ".orf", ".rw2", ".raf", ".pef", ".srw"}
AUDIO_EXTENSIONS = {".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma", ".m4a"}
SIDECAR_EXTENSIONS = {".xmp", ".thm", ".pp3", ".on1", ".cos", ".nks", ".nka", ".xml"}

ALL_MEDIA = PHOTO_EXTENSIONS | VIDEO_EXTENSIONS | RAW_EXTENSIONS | AUDIO_EXTENSIONS


def _get_file_category(suffix: str) -> str:
    if suffix in PHOTO_EXTENSIONS:
        return "photo"
    if suffix in VIDEO_EXTENSIONS:
        return "video"
    if suffix in RAW_EXTENSIONS:
        return "raw"
    if suffix in AUDIO_EXTENSIONS:
        return "audio"
    return "other"


def _stem_similarity(a: str, b: str) -> float:
    """Simple fuzzy similarity between two strings."""
    if a == b:
        return 1.0
    shorter = min(len(a), len(b))
    if shorter == 0:
        return 0.0
    matches = sum(1 for i in range(shorter) if a[i] == b[i])
    return matches / max(len(a), len(b))


def _emit(payload: dict) -> None:
    print(json.dumps(payload, indent=2, ensure_ascii=False))


def _fail(message: str, exit_code: int = 1) -> int:
    print(json.dumps({"error": message}), file=sys.stderr)
    return exit_code


def cmd_browse() -> int:
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        return _fail(f"Invalid JSON: {exc}")

    root = Path(payload.get("root_dir", ""))
    if not str(root) or not root.exists():
        return _fail("root_dir required and must exist")

    max_depth = payload.get("max_depth", 3)
    date_from = payload.get("date_from")
    date_to = payload.get("date_to")
    file_types = payload.get("file_types")
    include_sidecars = payload.get("include_sidecars", False)

    media_files: list[dict] = []
    all_files_map: dict[str, dict] = {}

    for current, dirs, filenames in os.walk(root):
        depth = len(Path(current).relative_to(root).parts)
        if depth > max_depth:
            dirs[:] = []
            continue
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for f in sorted(filenames):
            fp = Path(current) / f
            suffix = fp.suffix.lower()

            try:
                size = fp.stat().st_size
                mtime = fp.stat().st_mtime
            except OSError:
                size = 0
                mtime = 0

            if suffix in ALL_MEDIA:
                if file_types:
                    cat = _get_file_category(suffix)
                    if cat not in file_types:
                        continue

                if date_from or date_to:
                    mtime_dt = _dt.datetime.fromtimestamp(mtime, tz=_dt.timezone.utc)
                    if date_from:
                        from_dt = _dt.datetime.fromisoformat(date_from)
                        if mtime_dt < from_dt.replace(tzinfo=_dt.timezone.utc):
                            continue
                    if date_to:
                        to_dt = _dt.datetime.fromisoformat(date_to) + _dt.timedelta(days=1)
                        if mtime_dt >= to_dt.replace(tzinfo=_dt.timezone.utc):
                            continue

                media_files.append({
                    "path": str(fp),
                    "name": f,
                    "relative": str(fp.relative_to(root)),
                    "size": size,
                    "suffix": suffix,
                    "modified": _dt.datetime.fromtimestamp(mtime, tz=_dt.timezone.utc).isoformat(),
                    "category": _get_file_category(suffix),
                    "sidecars": [],
                })
            elif suffix in SIDECAR_EXTENSIONS:
                all_files_map[str(fp)] = {
                    "path": str(fp),
                    "name": f,
                    "relative": str(fp.relative_to(root)),
                    "suffix": suffix,
                    "size": size,
                }
            elif include_sidecars:
                all_files_map[str(fp)] = {
                    "path": str(fp),
                    "name": f,
                    "relative": str(fp.relative_to(root)),
                    "suffix": suffix,
                    "size": size,
                }

    # Smart sidecar matching
    for media in media_files:
        media_path = Path(media["path"])
        media_stem = media_path.stem.lower()
        media_dir = media_path.parent

        for sf_path_str, sf_data in list(all_files_map.items()):
            sf_path = Path(sf_path_str)
            sf_stem = sf_path.stem.lower()

            # Match 1: exact stem match (photo.jpg + photo.xmp)
            if sf_stem == media_stem:
                media["sidecars"].append(sf_data)
                del all_files_map[sf_path_str]
                continue

            # Match 2: stem starts with same prefix (IMG_0001.jpg + IMG_0001_edit.xmp)
            if sf_stem.startswith(media_stem) and sf_path.parent == media_dir:
                media["sidecars"].append(sf_data)
                del all_files_map[sf_path_str]
                continue

            # Match 3: fuzzy — same directory, stem similarity > 80%
            if sf_path.parent == media_dir and _stem_similarity(media_stem, sf_stem) > 0.8:
                media["sidecars"].append(sf_data)
                del all_files_map[sf_path_str]

    other_files_count = len(all_files_map)

    page = payload.get("page", 0)
    page_size = payload.get("page_size", 0)
    total_count = len(media_files)

    if page_size > 0:
        start = page * page_size
        end = start + page_size
        paged_files = media_files[start:end]
    else:
        paged_files = media_files

    _emit({
        "kind": "browse",
        "root": str(root),
        "file_count": total_count,
        "other_count": other_files_count,
        "page": page,
        "page_size": page_size if page_size > 0 else total_count,
        "total_pages": (total_count + page_size - 1) // page_size if page_size > 0 else 1,
        "depth": max_depth,
        "files": paged_files,
        "applied_filters": {
            "date_from": date_from,
            "date_to": date_to,
            "file_types": file_types,
        },
    })
    return 0


def build_parser() -> _ap.ArgumentParser:
    parser = _ap.ArgumentParser(prog="media_manager.bridge_library")
    parser.add_argument("action", choices=["browse"])
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv or sys.argv[1:])
    return cmd_browse() if args.action == "browse" else 1


if __name__ == "__main__":
    raise SystemExit(main())
