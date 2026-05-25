"""People face recognition bridge for the Tauri desktop app."""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

from media_manager.core.people_recognition import (
    PeopleScanConfig,
    scan_people,
    load_people_catalog,
)


def _emit(payload: dict) -> None:
    print(json.dumps(payload, indent=2, ensure_ascii=False))


def _fail(message: str, exit_code: int = 1) -> int:
    print(json.dumps({"error": message}), file=sys.stderr)
    return exit_code


def cmd_scan() -> int:
    raw = sys.stdin.read()
    if not raw.strip():
        return _fail("Empty stdin.")
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        return _fail(f"Invalid JSON: {exc}")

    try:
        options = PeopleScanConfig(
            source_dirs=[Path(p) for p in payload.get("source_dirs", [])],
            catalog_path=Path(payload["catalog_path"]) if payload.get("catalog_path") else None,
            tolerance=payload.get("tolerance", 0.6),
            backend=payload.get("backend", "auto"),
        )
    except (TypeError, ValueError) as exc:
        return _fail(f"Invalid options: {exc}")

    try:
        result = scan_people(options)
    except Exception as exc:
        return _fail(f"People scan failed: {exc}")

    result_dict = result.to_dict()
    summary = result_dict.get("summary", {})

    entries_map: dict[Path, dict] = defaultdict(lambda: {"face_count": 0, "matched_count": 0})
    for detection in result.detections:
        p = detection.path
        entries_map[p]["source_path"] = str(p)
        entries_map[p]["face_count"] += 1
        if detection.match is not None:
            entries_map[p]["matched_count"] += 1

    _emit({
        "kind": "scan_result",
        "total_faces": summary.get("face_count", 0),
        "matched_faces": summary.get("matched_faces", 0),
        "unknown_faces": summary.get("unknown_faces", 0),
        "people_count": summary.get("catalog_person_count", 0),
        "image_count": summary.get("image_files", 0),
        "entries": list(entries_map.values()),
    })
    return 0


def cmd_catalog_info() -> int:
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        return _fail(f"Invalid JSON: {exc}")

    catalog_path = Path(payload.get("catalog_path", ""))
    if not str(catalog_path):
        return _fail("catalog_path is required.")

    try:
        catalog = load_people_catalog(catalog_path)
    except Exception as exc:
        return _fail(f"Failed to load catalog: {exc}")

    _emit({
        "kind": "catalog_info",
        "path": str(catalog_path),
        "person_count": len(catalog.persons),
        "people": [
            {"person_id": p.person_id, "name": p.name, "face_count": len(p.embeddings)}
            for p in sorted(catalog.persons.values(), key=lambda x: x.person_id)
        ],
    })
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="media_manager.bridge_people")
    parser.add_argument("action", choices=["scan", "catalog-info"])
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv or sys.argv[1:])
    return cmd_scan() if args.action == "scan" else cmd_catalog_info()


if __name__ == "__main__":
    raise SystemExit(main())
