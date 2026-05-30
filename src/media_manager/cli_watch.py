from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

from .core.organizer import (
    DEFAULT_ORGANIZE_PATTERN,
    OrganizePlannerOptions,
    build_organize_dry_run,
    execute_organize_plan,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="media-manager watch",
        description="Watch a directory for changes and auto-organize new files.",
        epilog=(
            "Examples:\n"
            "  media-manager watch --source ~/Photos\n"
            "  media-manager watch --source ~/Photos --target ~/Organized\n"
            "  media-manager watch --source ~/Photos --target ~/Organized --move --interval 10\n"
        ),
    )
    parser.add_argument(
        "--source",
        type=Path,
        required=True,
        help="Source directory to watch.",
    )
    parser.add_argument(
        "--target",
        type=Path,
        required=False,
        help="Optional target directory for auto-organize. If omitted, only reports changes.",
    )
    parser.add_argument(
        "--pattern",
        default=DEFAULT_ORGANIZE_PATTERN,
        help="Target directory pattern for auto-organize.",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=5,
        help="Polling interval in seconds (default: 5).",
    )
    parser.add_argument(
        "--move",
        action="store_true",
        help="Use move instead of copy when auto-organizing.",
    )
    parser.add_argument(
        "--non-recursive",
        action="store_true",
        help="Only watch the top level of the source directory.",
    )
    parser.add_argument(
        "--include-hidden",
        action="store_true",
        help="Include hidden files and hidden folders.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print machine-readable JSON output for each change event.",
    )
    return parser


def _scan_files(source: Path, *, recursive: bool, include_hidden: bool) -> dict[str, float]:
    result: dict[str, float] = {}
    iterator = source.rglob("*") if recursive else source.glob("*")
    for f in iterator:
        if f.is_file():
            if not include_hidden and (
                any(part.startswith(".") for part in f.parts)
                or (f.name.startswith("."))
            ):
                continue
            try:
                result[str(f)] = f.stat().st_mtime
            except OSError:
                pass
    return result


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    source = Path(args.source)
    if not source.exists():
        msg = f"Error: source directory not found: {source}. Use --source to specify a valid directory."
        if args.json:
            print(json.dumps({"status": "error", "message": msg}))
        else:
            print(msg, file=sys.stderr)
        return 1

    use_json = args.json or os.environ.get("MEDIA_MANAGER_JSON") == "1"
    use_quiet = os.environ.get("MEDIA_MANAGER_QUIET") == "1"

    if not use_quiet:
        print(f"Watching {source} for changes... (Ctrl+C to stop)")
        if args.target:
            print(f"Auto-organize target: {args.target}")

    recursive = not args.non_recursive
    known_mtimes = _scan_files(source, recursive=recursive, include_hidden=args.include_hidden)

    try:
        while True:
            current_mtimes = _scan_files(source, recursive=recursive, include_hidden=args.include_hidden)
            new_files = []
            changed_files = []

            for path_str, mtime in current_mtimes.items():
                if path_str not in known_mtimes:
                    new_files.append(path_str)
                    known_mtimes[path_str] = mtime
                elif known_mtimes[path_str] != mtime:
                    changed_files.append(path_str)
                    known_mtimes[path_str] = mtime

            if new_files or changed_files:
                if use_json:
                    print(json.dumps({
                        "timestamp": time.strftime("%H:%M:%S"),
                        "new_files": new_files,
                        "changed_files": changed_files,
                    }))
                elif not use_quiet:
                    for f in new_files:
                        rel = Path(f).relative_to(source)
                        print(f"  NEW: {rel}")
                    for f in changed_files:
                        rel = Path(f).relative_to(source)
                        print(f"  MODIFIED: {rel}")
                    print(f"  Changes detected at {time.strftime('%H:%M:%S')}")

                if args.target and new_files:
                    if not use_quiet:
                        print("  Auto-organizing new files...")
                    plan = build_organize_dry_run(
                        OrganizePlannerOptions(
                            source_dirs=(source,),
                            target_root=args.target,
                            pattern=args.pattern,
                            recursive=recursive,
                            include_hidden=args.include_hidden,
                            operation_mode="move" if args.move else "copy",
                        )
                    )
                    if plan.planned_count > 0:
                        exec_result = execute_organize_plan(plan)
                        if use_json:
                            print(json.dumps({
                                "timestamp": time.strftime("%H:%M:%S"),
                                "organized": exec_result.executed_count,
                                "copied": exec_result.copied_count,
                                "moved": exec_result.moved_count,
                            }))
                        elif not use_quiet:
                            print(f"    Organized {exec_result.executed_count} files")
                    elif not use_quiet:
                        print("    No files to organize")

            time.sleep(args.interval)
    except KeyboardInterrupt:
        if use_json:
            print(json.dumps({"status": "stopped", "reason": "KeyboardInterrupt"}))
        elif not use_quiet:
            print("\nStopped watching.")
        return 0
