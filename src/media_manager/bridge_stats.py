"""Library statistics bridge for the Tauri desktop app."""

from __future__ import annotations

import argparse as _ap
import json
import logging
import sys
from collections import Counter
from pathlib import Path

from media_manager.bridge_base import emit as _emit, fail as _fail, read_stdin_json
from media_manager.sorter import iter_media_files
from media_manager.exiftool import read_exiftool_metadata_batch

logger = logging.getLogger(__name__)


def cmd_library_stats() -> int:
    payload = read_stdin_json()
    source_dir = Path(payload["source_dir"])
    sample_limit = payload.get("sample_limit", 500)

    files = list(iter_media_files([source_dir]))
    if not files:
        _emit({"total_files": 0, "total_size_bytes": 0, "by_extension": {}, "by_camera": {}, "by_year": {}, "by_month": {}, "oldest_file": None, "newest_file": None})
        return 0

    total_size = 0
    oldest = None
    newest = None
    by_extension: Counter[str] = Counter()

    for f in files:
        by_extension[f.suffix.lower()] += 1
        try:
            st = f.stat()
            total_size += st.st_size
            mtime = st.st_mtime
            if oldest is None or mtime < oldest[0]:
                oldest = (mtime, str(f), f.name)
            if newest is None or mtime > newest[0]:
                newest = (mtime, str(f), f.name)
        except OSError:
            pass

    sample = files[:sample_limit]
    meta_map = read_exiftool_metadata_batch(sample)

    by_camera: Counter[str] = Counter()
    by_year: Counter[str] = Counter()
    by_month: Counter[str] = Counter()

    for f in sample:
        meta = meta_map.get(f, {})
        camera = meta.get("Model")
        if camera:
            by_camera[str(camera)] += 1
        else:
            by_camera["Unknown"] += 1

        for tag in ("DateTimeOriginal", "SubSecDateTimeOriginal", "CreateDate", "DateCreated", "MediaCreateDate", "ContentCreateDate"):
            date_val = meta.get(tag)
            if date_val:
                try:
                    ds = str(date_val)
                    year = ds[:4]
                    month = ds[:7]
                    if year.isdigit() and int(year) >= 1900:
                        by_year[year] += 1
                        by_month[month] += 1
                        break
                except (ValueError, IndexError):
                    continue

    stats = {
        "total_files": len(files),
        "total_size_bytes": total_size,
        "by_extension": dict(by_extension.most_common()),
        "by_camera": dict(by_camera.most_common()),
        "by_year": dict(sorted(by_year.items())),
        "by_month": dict(sorted(by_month.items())),
        "oldest_file": {"path": oldest[1], "name": oldest[2]} if oldest else None,
        "newest_file": {"path": newest[1], "name": newest[2]} if newest else None,
    }
    _emit(stats)
    return 0


def cmd_size_report() -> int:
    payload = read_stdin_json()
    source_dir = Path(payload["source_dir"])
    top_n = payload.get("top_n", 50)

    files = list(iter_media_files([source_dir]))
    if not files:
        _emit({"largest_files": [], "total_size_bytes": 0, "file_count": 0})
        return 0

    sized: list[tuple[int, str, str]] = []
    total_size = 0
    for f in files:
        try:
            st = f.stat()
            total_size += st.st_size
            sized.append((st.st_size, str(f), f.name))
        except OSError:
            pass

    sized.sort(key=lambda x: -x[0])
    largest = sized[:top_n]

    size_counter: Counter[int] = Counter()
    for sz, _, _ in sized:
        size_counter[sz] += 1

    duplicate_space = sum(sz * (cnt - 1) for sz, cnt in size_counter.items() if cnt > 1)

    _emit({
        "largest_files": [{"path": p, "name": n, "size_bytes": s} for s, p, n in largest],
        "total_size_bytes": total_size,
        "file_count": len(files),
        "duplicate_space_wasted_bytes": duplicate_space,
    })
    return 0


def build_parser() -> _ap.ArgumentParser:
    parser = _ap.ArgumentParser(prog="media_manager.bridge_stats")
    parser.add_argument("action", choices=["stats", "size-report"])
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv or sys.argv[1:])
    if args.action == "stats":
        return cmd_library_stats()
    if args.action == "size-report":
        return cmd_size_report()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
