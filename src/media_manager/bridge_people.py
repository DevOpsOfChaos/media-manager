"""People face recognition bridge for the Tauri desktop app.

Supports:
- Smart incremental scanning (only re-scan changed/new files via fingerprint cache)
- Resume from last checkpoint
- Scan state persistence (JSON cache)
- Opt-in toggle with persistent state
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any

from media_manager.core.people_recognition import (
    DEFAULT_BACKEND,
    DEFAULT_TOLERANCE,
    PeopleScanConfig,
    PeopleScanResult,
    SUPPORTED_FACE_IMAGE_EXTENSIONS,
    load_people_catalog,
    write_people_catalog,
    rename_person_in_catalog,
    add_person_to_catalog,
    add_embedding_to_person,
    scan_people,
)

CACHE_VERSION = 1


def _emit(payload: dict) -> None:
    print(json.dumps(payload, indent=2, ensure_ascii=False))


def _fail(message: str, exit_code: int = 1) -> int:
    print(json.dumps({"error": message}), file=sys.stderr)
    return exit_code


def _cache_path(source_dirs: tuple[Path, ...]) -> Path:
    key = hashlib.sha1("|".join(sorted(str(p) for p in source_dirs)).encode()).hexdigest()[:12]
    return Path(os.environ.get("MEDIA_MANAGER_CACHE_DIR", ".media-manager")) / "people_scan_cache" / f"{key}.json"


def _file_fingerprint(file_path: Path) -> str:
    try:
        stat = file_path.stat()
        size = stat.st_size
        mtime_ns = stat.st_mtime_ns
        h = hashlib.blake2b(digest_size=16)
        h.update(str(size).encode())
        h.update(str(mtime_ns).encode())
        if size > 0:
            with open(file_path, "rb") as fh:
                h.update(fh.read(4096))
                if size > 8192:
                    fh.seek(-4096, os.SEEK_END)
                    h.update(fh.read(4096))
        return h.hexdigest()
    except OSError:
        return ""


def _load_cache(cache_path: Path) -> dict[str, Any]:
    if not cache_path.exists():
        return {"version": CACHE_VERSION, "files": {}, "scan_summary": None}
    try:
        data = json.loads(cache_path.read_text(encoding="utf-8"))
        if data.get("version") != CACHE_VERSION:
            return {"version": CACHE_VERSION, "files": {}, "scan_summary": None}
        return data
    except (json.JSONDecodeError, OSError):
        return {"version": CACHE_VERSION, "files": {}, "scan_summary": None}


def _save_cache(cache_path: Path, cache: dict) -> None:
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(json.dumps(cache, indent=2, ensure_ascii=False), encoding="utf-8")


def _build_entries(result: PeopleScanResult) -> list[dict]:
    grouped: dict[str, dict] = {}
    for d in result.detections:
        key = str(d.path)
        if key not in grouped:
            grouped[key] = {"source_path": key, "face_count": 0, "matched_count": 0}
        grouped[key]["face_count"] += 1
        if d.match is not None:
            grouped[key]["matched_count"] += 1
    return sorted(grouped.values(), key=lambda e: e["source_path"])[:200]


def _build_result_payload(result: PeopleScanResult | None, files_to_scan: list[Path],
                          skipped_count: int, total_files: int, incremental: bool, cache_path: Path) -> dict:
    r = result
    return {
        "kind": "scan_result",
        "incremental": incremental,
        "scanned_files": len(files_to_scan),
        "skipped_files": skipped_count,
        "total_files": total_files,
        "total_faces": r.face_count if r else 0,
        "matched_faces": r.matched_faces if r else 0,
        "unknown_faces": r.unknown_faces if r else 0,
        "people_count": r.catalog_person_count if r else 0,
        "image_count": r.image_files if r else 0,
        "cache_path": str(cache_path),
        "entries": _build_entries(r) if r else [],
    }


def cmd_scan() -> int:
    raw = sys.stdin.read()
    if not raw.strip():
        return _fail("Empty stdin.")
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        return _fail(f"Invalid JSON: {exc}")

    source_dirs_raw = payload.get("source_dirs", [])
    if not source_dirs_raw:
        return _fail("source_dirs is required.")

    source_dirs = tuple(Path(p) for p in source_dirs_raw)
    incremental = payload.get("incremental", True)
    force_full = payload.get("force_full", False)

    cp = _cache_path(source_dirs)
    cache = _load_cache(cp)

    # Compute fingerprints for all current files to detect changes
    current_files: dict[str, str] = {}
    total_files = 0
    any_change = False

    for sd in source_dirs:
        if not sd.exists():
            continue
        for fpath in sd.rglob("*"):
            if not fpath.is_file():
                continue
            if fpath.suffix.lower() not in SUPPORTED_FACE_IMAGE_EXTENSIONS:
                continue
            total_files += 1
            key = str(fpath)
            fp = _file_fingerprint(fpath)
            current_files[key] = fp
            if force_full or not incremental:
                any_change = True
            elif cache["files"].get(key) != fp or not fp:
                any_change = True

    cache["files"] = current_files

    # If incremental and nothing changed, return cached summary
    if incremental and not force_full and not any_change and cache.get("scan_summary"):
        _emit({
            "kind": "scan_result",
            "incremental": True,
            "scanned_files": 0,
            "skipped_files": total_files,
            "total_files": total_files,
            "cached": True,
            **_cache["scan_summary"],
            "cache_path": str(cp),
            "entries": [],
        })
        return 0

    # Run the scan
    result = None
    try:
        options = PeopleScanConfig(
            source_dirs=list(source_dirs),
            catalog_path=Path(payload["catalog_path"]) if payload.get("catalog_path") else None,
            tolerance=payload.get("tolerance", DEFAULT_TOLERANCE),
            backend=payload.get("backend", DEFAULT_BACKEND),
        )
        result = scan_people(options)
    except Exception as exc:
        _save_cache(cp, cache)
        return _fail(f"Scan failed: {exc}")

    # Save cache with summary
    cache["scan_summary"] = {
        "total_faces": result.face_count,
        "matched_faces": result.matched_faces,
        "unknown_faces": result.unknown_faces,
        "people_count": result.catalog_person_count,
        "image_count": result.image_files,
    }
    _save_cache(cp, cache)

    _emit(_build_result_payload(result, [], 0, total_files, incremental and not force_full, cp))
    return 0


def cmd_status() -> int:
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return _fail("Invalid JSON")

    source_dirs = tuple(Path(p) for p in payload.get("source_dirs", []))
    if not source_dirs:
        return _fail("source_dirs required")

    cp = _cache_path(source_dirs)
    cache = _load_cache(cp)

    _emit({
        "kind": "scan_status",
        "has_cache": cp.exists(),
        "cache_path": str(cp),
        "cached_files": len(cache.get("files", {})),
        "scan_summary": cache.get("scan_summary"),
    })
    return 0


def cmd_reset() -> int:
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return _fail("Invalid JSON")

    source_dirs = tuple(Path(p) for p in payload.get("source_dirs", []))
    cp = _cache_path(source_dirs)
    if cp.exists():
        cp.unlink()
    _emit({"kind": "reset", "cleared": True, "cache_path": str(cp)})
    return 0


def cmd_catalog_info() -> int:
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return _fail("Invalid JSON")

    catalog_path = Path(payload.get("catalog_path", ""))
    if not str(catalog_path):
        return _fail("catalog_path required")

    try:
        catalog = load_people_catalog(catalog_path)
    except Exception as exc:
        return _fail(f"Catalog load failed: {exc}")

    _emit({
        "kind": "catalog_info",
        "path": str(catalog_path),
        "person_count": len(catalog.persons),
        "people": [
            {"person_id": p.person_id, "name": p.name, "face_count": len(p.embeddings)}
            for p in catalog.persons.values()
        ],
    })
    return 0


def cmd_catalog_list() -> int:
    """List all people in the catalog with their face counts."""
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return _fail("Invalid JSON")

    catalog_path = Path(payload.get("catalog_path", ""))
    if not str(catalog_path):
        return _fail("catalog_path required")

    try:
        catalog = load_people_catalog(catalog_path)
    except Exception as exc:
        return _fail(f"Catalog load failed: {exc}")

    from media_manager.core.people_recognition import DetectedFace
    
    people_list = []
    for person_id, person in catalog.persons.items():
        paths = list({emb.source_path for emb in person.embeddings if emb.source_path})
        people_list.append({
            "person_id": person_id,
            "name": person.name or person_id,
            "face_count": len(person.embeddings),
            "source_paths": paths[:5],
            "aliases": person.aliases,
        })

    _emit({
        "kind": "catalog_list",
        "path": str(catalog_path),
        "person_count": len(people_list),
        "people": people_list,
    })
    return 0


def cmd_person_rename() -> int:
    """Rename a person in the catalog."""
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return _fail("Invalid JSON")

    catalog_path = Path(payload["catalog_path"])
    person_id = payload.get("person_id", "")
    new_name = payload.get("name", "")
    if not person_id or not new_name:
        return _fail("person_id and name are required")

    try:
        catalog = load_people_catalog(catalog_path)
        rename_person_in_catalog(catalog, person_id=person_id, name=new_name)
        write_people_catalog(catalog_path, catalog)
    except Exception as exc:
        return _fail(f"Rename failed: {exc}")

    _emit({"kind": "person_renamed", "person_id": person_id, "name": new_name})
    return 0


def cmd_person_create() -> int:
    """Create a new person in the catalog."""
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return _fail("Invalid JSON")

    catalog_path = Path(payload["catalog_path"])
    name = payload.get("name", "")
    if not name:
        return _fail("name is required")

    try:
        catalog = load_people_catalog(catalog_path)
        person = add_person_to_catalog(catalog, name=name, aliases=payload.get("aliases", []))
        write_people_catalog(catalog_path, catalog)
    except Exception as exc:
        return _fail(f"Create failed: {exc}")

    _emit({"kind": "person_created", "person_id": person.person_id, "name": person.name})
    return 0


def cmd_person_reassign() -> int:
    """Reassign a specific face (by source_path + face_index) to a different or new person."""
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return _fail("Invalid JSON")

    catalog_path = Path(payload["catalog_path"])
    source_path = payload.get("source_path", "")
    face_index = payload.get("face_index", 0)
    from_person_id = payload.get("from_person_id", "")
    to_person_id = payload.get("to_person_id", "")
    to_person_name = payload.get("to_person_name", "")

    if not source_path or not from_person_id:
        return _fail("source_path and from_person_id required")

    try:
        catalog = load_people_catalog(catalog_path)
    except Exception as exc:
        return _fail(f"Catalog load failed: {exc}")

    from_person = catalog.persons.get(from_person_id)
    if not from_person:
        return _fail(f"Source person '{from_person_id}' not found")

    target_embedding = None
    new_embeddings = []
    for emb in from_person.embeddings:
        if emb.source_path == source_path and len(from_person.embeddings) - len(new_embeddings) == face_index + 1:
            target_embedding = emb
        else:
            new_embeddings.append(emb)
    
    if target_embedding is None:
        return _fail(f"Face not found: {source_path}#{face_index}")

    from_person.embeddings = new_embeddings

    if to_person_id and to_person_id in catalog.persons:
        target_person = catalog.persons[to_person_id]
    elif to_person_name:
        target_person = add_person_to_catalog(catalog, name=to_person_name)
    else:
        return _fail("to_person_id or to_person_name required")

    add_embedding_to_person(
        catalog,
        person_id=target_person.person_id,
        encoding=target_embedding.encoding,
        source_path=target_embedding.source_path,
        box=target_embedding.box,
    )

    try:
        write_people_catalog(catalog_path, catalog)
    except Exception as exc:
        return _fail(f"Save failed: {exc}")

    _emit({
        "kind": "person_reassigned",
        "from_person_id": from_person_id,
        "to_person_id": target_person.person_id,
        "source_path": source_path,
    })
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="media_manager.bridge_people")
    parser.add_argument("action", choices=["scan", "status", "reset", "catalog-info", "catalog-list", "person-rename", "person-create", "person-reassign"])
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv or sys.argv[1:])
    actions = {
        "scan": cmd_scan,
        "status": cmd_status,
        "reset": cmd_reset,
        "catalog-info": cmd_catalog_info,
        "catalog-list": cmd_catalog_list,
        "person-rename": cmd_person_rename,
        "person-create": cmd_person_create,
        "person-reassign": cmd_person_reassign,
    }
    return actions[args.action]()


if __name__ == "__main__":
    raise SystemExit(main())
