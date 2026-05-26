"""Library browser bridge for the Tauri desktop app."""

from __future__ import annotations

import argparse as _ap
import datetime as _dt
import hashlib
import json
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

    # --- Phase 2: Cached paginated load ---
    # Try SQLite MediaCache first (instant, no walk needed on repeat access)
    media_files: list[dict] = []
    cache_valid = False
    cache_data: dict = {}
    try:
        from media_manager.core.media_cache import MediaCache
        mc = MediaCache.get()
        mc._ensure_schema()
        source_root_str = str(root)
        row = mc._conn().execute("SELECT value FROM cache_meta WHERE key='last_sync'").fetchone()
        last_sync = float(row[0]) if row else 0
        if time.time() - last_sync > 60:
            mc.sync([source_root_str])
            mc._conn().execute(
                "INSERT OR REPLACE INTO cache_meta(key,value) VALUES('last_sync',?)",
                (str(time.time()),)
            )
            mc._conn().commit()
        cached_rows = mc.get_scanned_files([source_root_str])
        if cached_rows:
            cache_valid = True
            for sf in cached_rows:
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
        pass

    # Fallback to JSON file cache if SQLite cache didn't populate
    if not media_files:
        cache_dir = Path(os.environ.get("MEDIA_MANAGER_HOME", Path.home() / ".media-manager")) / "cache"
        cache_dir.mkdir(parents=True, exist_ok=True)
        root_hash = hashlib.md5(str(root.resolve()).encode()).hexdigest()[:12]
        cache_path = cache_dir / f"library_{root_hash}.json"

        if cache_path.exists():
            try:
                cache_data = json.loads(cache_path.read_text())
                cache_age = time.time() - cache_data.get("created_at", 0)
                if cache_data.get("root") == str(root) and cache_age < 300:
                    cache_valid = True
                    media_files = cache_data["files"]
            except Exception:
                pass

        if not media_files:
            media_files = _scan_directory(root, max_depth, date_from, date_to, file_types)
            cache_data = {
                "root": str(root),
                "created_at": time.time(),
                "file_count": len(media_files),
                "files": media_files,
            }
            cache_path.write_text(json.dumps(cache_data, ensure_ascii=False))

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
        "other_count": cache_data.get("other_count", 0) if cache_valid else 0,
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
