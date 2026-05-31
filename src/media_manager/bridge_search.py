"""Full-text search bridge for the Tauri desktop app."""

from __future__ import annotations

import argparse as _ap
import json
import logging
import sys
from pathlib import Path

from media_manager.bridge_base import emit as _emit, fail as _fail, read_stdin_json
from media_manager.sorter import iter_media_files
from media_manager.exiftool import read_exiftool_metadata_batch

logger = logging.getLogger(__name__)

DATE_TAGS = (
    "DateTimeOriginal", "SubSecDateTimeOriginal", "CreateDate", "DateCreated",
    "MediaCreateDate", "ContentCreateDate", "ModifyDate", "FileModifyDate",
)


def _extract_date(meta: dict) -> str:
    for tag in DATE_TAGS:
        val = meta.get(tag)
        if val:
            return str(val)
    return ""


def cmd_search() -> int:
    payload = read_stdin_json()
    source_dir = Path(payload["source_dir"])
    query = payload.get("query", "").lower()
    search_fields = payload.get("fields", ["filename", "path", "camera", "date"])
    max_results = min(payload.get("max_results", 50), 200)

    if not query:
        return _fail("query is required")

    files = list(iter_media_files([source_dir]))
    total_matches = 0
    results: list[dict] = []

    need_metadata = "camera" in search_fields or "date" in search_fields
    meta_map: dict[Path, dict] = {}
    if need_metadata and files:
        meta_map = read_exiftool_metadata_batch(files[:200])

    for f in files:
        score = 0
        if "filename" in search_fields and query in f.name.lower():
            score += 10
            if f.name.lower().startswith(query):
                score += 5
        if "path" in search_fields and query in str(f).lower():
            score += 5
            if f.stem.lower() == query:
                score += 3

        if need_metadata and score > 0:
            meta = meta_map.get(f, {})
            if "camera" in search_fields:
                camera = meta.get("Model")
                if camera and query in str(camera).lower():
                    score += 5
            if "date" in search_fields:
                date_val = _extract_date(meta)
                if date_val and query in date_val.lower():
                    score += 5

        if score > 0:
            total_matches += 1
            entry = {"path": str(f), "name": f.name, "score": score}
            try:
                entry["size_bytes"] = f.stat().st_size
            except OSError:
                entry["size_bytes"] = 0
            if need_metadata:
                meta = meta_map.get(f, {})
                entry["camera"] = str(meta.get("Model", "")) or None
                entry["date"] = _extract_date(meta) or None
            results.append(entry)

    results.sort(key=lambda r: -r["score"])

    _emit({
        "query": query,
        "results": results[:max_results],
        "total_matches": total_matches,
    })
    return 0


def build_parser() -> _ap.ArgumentParser:
    parser = _ap.ArgumentParser(prog="media_manager.bridge_search")
    parser.add_argument("action", choices=["search"])
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv or sys.argv[1:])
    if args.action == "search":
        return cmd_search()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
