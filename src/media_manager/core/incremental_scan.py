"""Incremental scanner -- only scans new or modified files since last run."""

import json
import time
from pathlib import Path


def load_scan_state(state_path: Path) -> dict[str, float]:
    if state_path.exists():
        try:
            return json.loads(state_path.read_text())
        except Exception:
            pass
    return {}


def save_scan_state(state_path: Path, state: dict[str, float]) -> None:
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(state, indent=2))


def scan_incremental(source_dirs: list[Path], state_path: Path) -> dict:
    start = time.perf_counter()
    old_state = load_scan_state(state_path)
    new_state = {}

    new_files = []
    modified_files = []

    for source_dir in source_dirs:
        for f in source_dir.rglob("*"):
            if not f.is_file():
                continue
            try:
                mtime = f.stat().st_mtime
            except OSError:
                continue

            path_str = str(f)
            new_state[path_str] = mtime

            if path_str not in old_state:
                new_files.append(path_str)
            elif old_state[path_str] != mtime:
                modified_files.append(path_str)

    deleted_files = [p for p in old_state if p not in new_state]

    save_scan_state(state_path, new_state)

    return {
        "new_files": new_files,
        "modified_files": modified_files,
        "deleted_files": deleted_files,
        "total_scanned": len(new_state),
        "total_new": len(new_files),
        "total_modified": len(modified_files),
        "total_deleted": len(deleted_files),
        "scan_duration_seconds": round(time.perf_counter() - start, 2),
    }
