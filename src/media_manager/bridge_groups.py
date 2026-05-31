"""Smart grouping bridge for the Tauri desktop app.

Groups media files by date, camera model, GPS location, detected people,
and provides a chronological timeline.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from collections import defaultdict
from pathlib import Path

from media_manager.bridge_base import emit as _emit, fail as _fail

logger = logging.getLogger(__name__)


def _iter_files(source_dir: Path) -> list[Path]:
    from media_manager.sorter import iter_media_files
    return iter_media_files([source_dir])


def _read_batch_meta(files: list[Path]) -> dict[Path, dict]:
    from media_manager.exiftool import read_exiftool_metadata_batch
    return read_exiftool_metadata_batch(files, include_time_tags=True, group_names=False)


def _extract_date_value(meta: dict) -> str:
    for tag in ("DateTimeOriginal", "CreateDate", "MediaCreateDate", "DateCreated"):
        val = meta.get(tag)
        if isinstance(val, str) and val.strip():
            return val.strip()
    return ""


def _format_size(bytes_val: int) -> str:
    if bytes_val >= 1_073_741_824:
        return f"{bytes_val / 1_073_741_824:.1f} GB"
    if bytes_val >= 1_048_576:
        return f"{bytes_val / 1_048_576:.1f} MB"
    if bytes_val >= 1024:
        return f"{bytes_val / 1024:.1f} KB"
    return f"{bytes_val} B"


def cmd_group_by_date() -> int:
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError as exc:
        return _fail(f"Invalid JSON: {exc}")

    source_dir_raw = payload.get("source_dir", "")
    if not source_dir_raw:
        return _fail("source_dir is required")

    source_dir = Path(source_dir_raw)
    granularity = payload.get("granularity", "month")

    files = _iter_files(source_dir)
    sample_count = min(len(files), 2000)
    meta_map = _read_batch_meta(files[:sample_count])

    groups: dict[str, dict] = defaultdict(lambda: {"count": 0, "total_size": 0, "sample_paths": []})

    for f in files[:sample_count]:
        meta = meta_map.get(f, {})
        date_val = _extract_date_value(meta)

        if date_val and len(date_val) >= 4:
            if granularity == "year":
                key = date_val[:4]
            elif granularity == "month":
                key = date_val[:7] if len(date_val) >= 7 else date_val[:4]
            elif granularity == "day":
                key = date_val[:10] if len(date_val) >= 10 else (date_val[:7] if len(date_val) >= 7 else date_val[:4])
            else:
                key = date_val[:7]
        else:
            key = "unknown"

        g = groups[key]
        g["count"] += 1
        try:
            g["total_size"] += f.stat().st_size
        except OSError:
            pass
        if len(g["sample_paths"]) < 3:
            g["sample_paths"].append(str(f))

    sorted_groups = sorted(groups.items(), key=lambda kv: kv[0], reverse=True)

    return _emit({
        "kind": "group_by_date",
        "granularity": granularity,
        "total_files": len(files),
        "scanned_files": sample_count,
        "total_groups": len(groups),
        "formatted_sizes": {k: _format_size(v["total_size"]) for k, v in sorted_groups},
        "groups": {k: v for k, v in sorted_groups},
    })


def cmd_group_by_camera() -> int:
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError as exc:
        return _fail(f"Invalid JSON: {exc}")

    source_dir_raw = payload.get("source_dir", "")
    if not source_dir_raw:
        return _fail("source_dir is required")

    source_dir = Path(source_dir_raw)
    files = _iter_files(source_dir)
    sample_count = min(len(files), 2000)
    meta_map = _read_batch_meta(files[:sample_count])

    groups: dict[str, dict] = defaultdict(lambda: {"count": 0, "total_size": 0, "sample_paths": []})

    for f in files[:sample_count]:
        meta = meta_map.get(f, {})
        model = meta.get("Model")
        if isinstance(model, str) and model.strip():
            key = model.strip()
        else:
            key = "unknown"

        g = groups[key]
        g["count"] += 1
        try:
            g["total_size"] += f.stat().st_size
        except OSError:
            pass
        if len(g["sample_paths"]) < 3:
            g["sample_paths"].append(str(f))

    sorted_groups = sorted(groups.items(), key=lambda kv: kv[0])

    return _emit({
        "kind": "group_by_camera",
        "total_files": len(files),
        "scanned_files": sample_count,
        "total_groups": len(groups),
        "formatted_sizes": {k: _format_size(v["total_size"]) for k, v in sorted_groups},
        "groups": {k: v for k, v in sorted_groups},
    })


def cmd_group_by_location() -> int:
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError as exc:
        return _fail(f"Invalid JSON: {exc}")

    source_dir_raw = payload.get("source_dir", "")
    if not source_dir_raw:
        return _fail("source_dir is required")

    source_dir = Path(source_dir_raw)
    files = _iter_files(source_dir)
    sample_count = min(len(files), 2000)
    meta_map = _read_batch_meta(files[:sample_count])

    groups: dict[str, dict] = defaultdict(lambda: {"count": 0, "total_size": 0, "sample_paths": []})

    for f in files[:sample_count]:
        meta = meta_map.get(f, {})
        lat = meta.get("GPSLatitude")
        lon = meta.get("GPSLongitude")

        if isinstance(lat, (int, float)) and isinstance(lon, (int, float)):
            rounded_lat = round(float(lat), 2)
            rounded_lon = round(float(lon), 2)
            key = f"{rounded_lat:.2f},{rounded_lon:.2f}"
        else:
            key = "no_gps"

        g = groups[key]
        g["count"] += 1
        try:
            g["total_size"] += f.stat().st_size
        except OSError:
            pass
        if len(g["sample_paths"]) < 3:
            g["sample_paths"].append(str(f))

    sorted_groups = sorted(
        [(k, v) for k, v in groups.items() if k != "no_gps"],
        key=lambda kv: kv[1]["count"],
        reverse=True,
    )
    if "no_gps" in groups:
        sorted_groups.append(("no_gps", groups["no_gps"]))

    return _emit({
        "kind": "group_by_location",
        "total_files": len(files),
        "scanned_files": sample_count,
        "total_groups": len(groups),
        "formatted_sizes": {k: _format_size(v["total_size"]) for k, v in sorted_groups},
        "groups": {k: v for k, v in sorted_groups},
    })


def cmd_group_by_people() -> int:
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError as exc:
        return _fail(f"Invalid JSON: {exc}")

    catalog_path_raw = payload.get("catalog_path", "")
    if not catalog_path_raw:
        return _fail("catalog_path is required")

    try:
        from media_manager.core.people_recognition import load_people_catalog
        catalog = load_people_catalog(Path(catalog_path_raw), load_embeddings=True)
    except (OSError, ValueError, ImportError) as exc:
        return _fail(f"Failed to load catalog: {exc}")

    person_files: dict[str, dict] = {}
    for person_id, person in catalog.persons.items():
        paths: set[str] = set()
        for emb in person.embeddings:
            if emb.source_path:
                paths.add(emb.source_path)
        person_files[person_id] = {
            "name": person.name or person_id,
            "aliases": person.aliases,
            "file_count": len(paths),
            "sample_paths": sorted(paths)[:5],
        }

    return _emit({
        "kind": "group_by_people",
        "person_count": len(person_files),
        "people": person_files,
    })


def cmd_timeline() -> int:
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError as exc:
        return _fail(f"Invalid JSON: {exc}")

    source_dir_raw = payload.get("source_dir", "")
    if not source_dir_raw:
        return _fail("source_dir is required")

    source_dir = Path(source_dir_raw)
    granularity = payload.get("granularity", "month")

    files = _iter_files(source_dir)
    sample_count = min(len(files), 2000)
    meta_map = _read_batch_meta(files[:sample_count])

    groups: dict[str, dict] = defaultdict(
        lambda: {"count": 0, "total_size": 0, "sample_paths": [], "formatted_size": ""}
    )

    for f in files[:sample_count]:
        meta = meta_map.get(f, {})
        date_val = _extract_date_value(meta)

        if date_val and len(date_val) >= 4:
            if granularity == "year":
                key = date_val[:4]
            elif granularity == "month":
                key = date_val[:7] if len(date_val) >= 7 else date_val[:4]
            elif granularity == "day":
                key = date_val[:10] if len(date_val) >= 10 else (date_val[:7] if len(date_val) >= 7 else date_val[:4])
            else:
                key = date_val[:7]
        else:
            key = "unknown"

        g = groups[key]
        g["count"] += 1
        try:
            g["total_size"] += f.stat().st_size
        except OSError:
            pass
        if len(g["sample_paths"]) < 5:
            g["sample_paths"].append(str(f))

    timeline = []
    for key, group in sorted(groups.items()):
        group["date"] = key
        group["formatted_size"] = _format_size(group["total_size"])
        group.pop("total_size", None)
        timeline.append(group)

    return _emit({
        "kind": "timeline",
        "granularity": granularity,
        "total_files": len(files),
        "scanned_files": sample_count,
        "entries": timeline,
    })


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="media_manager.bridge_groups")
    parser.add_argument(
        "action",
        choices=["group-by-date", "group-by-camera", "group-by-location", "group-by-people", "timeline"],
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv or sys.argv[1:])
    actions = {
        "group-by-date": cmd_group_by_date,
        "group-by-camera": cmd_group_by_camera,
        "group-by-location": cmd_group_by_location,
        "group-by-people": cmd_group_by_people,
        "timeline": cmd_timeline,
    }
    return actions[args.action]()


if __name__ == "__main__":
    raise SystemExit(main())
