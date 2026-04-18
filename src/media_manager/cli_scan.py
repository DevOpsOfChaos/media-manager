from __future__ import annotations

import argparse
import json
from pathlib import Path

from .core.scanner import ScanOptions, scan_media_sources



def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="media-manager scan",
        description="Scan one or more source folders and list discovered media files.",
    )
    parser.add_argument(
        "sources",
        nargs="+",
        help="One or more source folders to scan.",
    )
    parser.add_argument(
        "--non-recursive",
        action="store_true",
        help="Only scan the top level of each source folder.",
    )
    parser.add_argument(
        "--include-hidden",
        action="store_true",
        help="Include hidden files and hidden folders.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print machine-readable JSON output.",
    )
    parser.add_argument(
        "--show-files",
        action="store_true",
        help="Print every discovered file in addition to the summary.",
    )
    return parser



def _build_summary_payload(summary) -> dict[str, object]:
    return {
        "sources": [str(path) for path in summary.source_dirs],
        "missing_sources": [str(path) for path in summary.missing_sources],
        "media_file_count": summary.media_file_count,
        "total_size_bytes": summary.total_size_bytes,
        "skipped_hidden_paths": summary.skipped_hidden_paths,
        "skipped_non_media_files": summary.skipped_non_media_files,
        "files": [
            {
                "source_root": str(item.source_root),
                "path": str(item.path),
                "relative_path": item.relative_path.as_posix(),
                "extension": item.extension,
                "size_bytes": item.size_bytes,
            }
            for item in summary.files
        ],
    }



def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    options = ScanOptions(
        source_dirs=tuple(Path(item) for item in args.sources),
        recursive=not args.non_recursive,
        include_hidden=args.include_hidden,
    )
    summary = scan_media_sources(options)

    if args.json:
        print(json.dumps(_build_summary_payload(summary), indent=2, ensure_ascii=False))
        return 0 if not summary.missing_sources else 1

    print("Media scan summary")
    print(f"  Sources: {summary.source_count}")
    print(f"  Missing sources: {len(summary.missing_sources)}")
    print(f"  Media files: {summary.media_file_count}")
    print(f"  Total size: {summary.total_size_bytes} bytes")
    print(f"  Skipped hidden paths: {summary.skipped_hidden_paths}")
    print(f"  Skipped non-media files: {summary.skipped_non_media_files}")

    if summary.missing_sources:
        print("\nMissing sources:")
        for path in summary.missing_sources:
            print(f"  - {path}")

    if args.show_files and summary.files:
        print("\nDiscovered media files:")
        for item in summary.files:
            print(f"  - {item.path}")

    return 0 if not summary.missing_sources else 1
