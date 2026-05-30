from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter
from pathlib import Path

from .core.cli_progress import cli_progress, cli_progress_done


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="media-manager stats",
        description="Print library statistics for a directory tree.",
        epilog=(
            "Examples:\n"
            "  media-manager stats --source ~/Photos\n"
            "  media-manager stats --source ~/Photos --top 10 --json\n"
            "  media-manager stats --source ~/Photos --non-recursive\n"
        ),
    )
    parser.add_argument(
        "--source",
        type=Path,
        required=True,
        help="Source directory to analyze.",
    )
    parser.add_argument(
        "--non-recursive",
        action="store_true",
        help="Only scan the top level of the source directory.",
    )
    parser.add_argument(
        "--include-hidden",
        action="store_true",
        help="Include hidden files and hidden folders.",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=15,
        help="Number of top extensions to display (default: 15).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print machine-readable JSON output.",
    )
    return parser


def _format_size(size_bytes: int) -> str:
    if size_bytes >= 1024**3:
        return f"{size_bytes / (1024**3):.1f} GB"
    elif size_bytes >= 1024**2:
        return f"{size_bytes / (1024**2):.1f} MB"
    elif size_bytes >= 1024:
        return f"{size_bytes / 1024:.1f} KB"
    return f"{size_bytes} B"


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    source = Path(args.source)
    if not source.exists():
        print(
            f"Error: source directory not found: {source}. "
            f"Use --source to specify a valid directory.",
            file=sys.stderr,
        )
        return 1

    use_json = args.json or os.environ.get("MEDIA_MANAGER_JSON") == "1"
    use_quiet = os.environ.get("MEDIA_MANAGER_QUIET") == "1"

    stats: Counter[str] = Counter()
    total_size = 0
    file_count = 0
    error_count = 0

    iterator = source.glob("*") if args.non_recursive else source.rglob("*")
    file_list = [
        f for f in iterator
        if f.is_file()
        and (args.include_hidden or not (
            any(part.startswith(".") for part in f.parts)
            or f.name.startswith(".")
        ))
    ]
    total_to_scan = len(file_list)

    for idx, f in enumerate(file_list):
        ext = f.suffix.lower() if f.suffix else "(no extension)"
        stats[ext] += 1
        try:
            total_size += f.stat().st_size
        except OSError:
            error_count += 1
        file_count += 1
        if not use_json and not use_quiet and idx % 50 == 0:
            cli_progress(idx + 1, total_to_scan, "Scanning")

    if not use_json and not use_quiet:
        cli_progress_done(f"Scanned {file_count:,} files")

    payload = {
        "source": str(source),
        "recursive": not args.non_recursive,
        "total_files": file_count,
        "total_size_bytes": total_size,
        "total_size_human": _format_size(total_size),
        "error_count": error_count,
        "extensions": [
            {"extension": ext, "count": count, "pct": round(count / file_count * 100, 1) if file_count else 0}
            for ext, count in stats.most_common(args.top)
        ],
        "unique_extensions": len(stats),
    }

    if use_json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0

    if not use_quiet:
        print(f"\nLibrary Statistics for: {source}")
        print(f"  Total files: {file_count:,}")
        print(f"  Total size:  {_format_size(total_size)}")
        if error_count:
            print(f"  Read errors: {error_count}")
        if stats:
            print(f"\n  Top {min(args.top, len(stats))} extensions (of {len(stats)} unique):")
            for ext, count in stats.most_common(args.top):
                pct = count / file_count * 100 if file_count else 0
                bar = "\u2588" * int(pct / 2)
                print(f"  {ext:<12} {count:>8,}  ({pct:5.1f}%)  {bar}")

    return 0


cmd_stats = main
