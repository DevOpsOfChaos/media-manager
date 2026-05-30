"""Library browser bridge for the Tauri desktop app."""

from __future__ import annotations

import argparse as _ap
import datetime as _dt
import json
import logging
import os
import sys
import time
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


from media_manager.bridge_base import emit as _emit, fail as _fail

logger = logging.getLogger(__name__)


def _scan_directory(root: Path, max_depth: int, date_from: str | None, date_to: str | None, file_types: list[str] | None) -> list[dict]:
    """Full directory scan — collects all media files with metadata."""
    media_files: list[dict] = []

    for current, dirs, filenames in os.walk(root):
        depth = len(Path(current).relative_to(root).parts)
        if depth > max_depth:
            dirs[:] = []
            continue
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for f in sorted(filenames):
            fp = Path(current) / f
            suffix = fp.suffix.lower()

            if suffix not in ALL_MEDIA:
                continue

            if file_types:
                cat = _get_file_category(suffix)
                if cat not in file_types:
                    continue

            try:
                st = fp.stat()
                size = st.st_size
                mtime = st.st_mtime
            except OSError:
                size = 0
                mtime = 0

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

    return media_files


def cmd_browse() -> int:
    """Browse a directory tree for media files from stdin JSON options."""
    logger.info("Browse: starting")
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        logger.error("Browse: invalid JSON: %s", exc)
        return _fail(f"Invalid JSON: {exc}")

    root = Path(payload.get("root_dir", ""))
    if not str(root) or not root.exists():
        return _fail("root_dir required and must exist")

    max_depth = payload.get("max_depth", 3)
    date_from = payload.get("date_from")
    date_to = payload.get("date_to")
    file_types = payload.get("file_types")
    page = payload.get("page", 0)
    page_size = payload.get("page_size", 0)
    quick = payload.get("quick", False)

    # --- Phase 1: Quick count ---
    if quick:
        media_count = 0
        other_count = 0
        for current, dirs, filenames in os.walk(root):
            depth = len(Path(current).relative_to(root).parts)
            if depth > max_depth:
                dirs[:] = []
                continue
            dirs[:] = [d for d in dirs if not d.startswith(".")]
            for f in filenames:
                suffix = Path(f).suffix.lower()
                if suffix in ALL_MEDIA:
                    media_count += 1
                else:
                    other_count += 1

        _emit({
            "kind": "browse",
            "root": str(root),
            "file_count": media_count,
            "other_count": other_count,
            "quick": True,
            "depth": max_depth,
        })
        return 0

    # --- Phase 2: Cached paginated load via MediaCache ---
    media_files: list[dict] = []
    cache_valid = False
    try:
        from media_manager.core.media_cache import MediaCache
        cache = MediaCache.get()
        cache._ensure_schema()
        source_root_str = str(root)
        row = cache._conn().execute("SELECT value FROM cache_meta WHERE key='last_sync'").fetchone()
        last_sync = float(row[0]) if row else 0
        if time.time() - last_sync > 60:
            cache.sync([source_root_str])
            cache._conn().execute(
                "INSERT OR REPLACE INTO cache_meta(key,value) VALUES('last_sync',?)",
                (str(time.time()),)
            )
            cache._conn().commit()
        scan_summary = cache.build_scan_summary([source_root_str])
        if scan_summary and scan_summary.files:
            cache_valid = True
            for sf in scan_summary.files:
                suffix = sf.extension
                cat = _get_file_category(suffix)
                if file_types and cat not in file_types:
                    continue
                media_files.append({
                    "path": str(sf.path),
                    "name": sf.path.name,
                    "relative": str(sf.relative_path),
                    "size": sf.size_bytes,
                    "suffix": suffix,
                    "modified": "",
                    "category": cat,
                    "sidecars": [],
                })
    except Exception:
        logger.exception("Browse: MediaCache load failed, falling back to directory scan")

    if not media_files:
        media_files = _scan_directory(root, max_depth, date_from, date_to, file_types)

    total_count = len(media_files)

    # Paginate
    if page_size > 0:
        start = page * page_size
        end = start + page_size
        paged_files = media_files[start:end]
    else:
        paged_files = media_files
        page_size = total_count

    _emit({
        "kind": "browse",
        "root": str(root),
        "file_count": total_count,
        "other_count": 0,
        "page": page,
        "page_size": page_size,
        "total_pages": max(1, (total_count + page_size - 1) // page_size) if page_size > 0 else 1,
        "depth": max_depth,
        "files": paged_files,
        "cached": cache_valid,
        "applied_filters": {
            "date_from": date_from,
            "date_to": date_to,
            "file_types": file_types,
        },
    })
    logger.info("Browse: complete, %d files (cached=%s)", total_count, cache_valid)
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
