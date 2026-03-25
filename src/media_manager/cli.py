from __future__ import annotations

import argparse
from pathlib import Path

from .sorter import SortConfig, organize_media


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="media-manager")
    subparsers = parser.add_subparsers(dest="command", required=True)

    organize = subparsers.add_parser("organize", help="Sort media files by resolved date")
    organize.add_argument("source", type=Path, help="Source directory")
    organize.add_argument("target", type=Path, help="Target directory")
    organize.add_argument(
        "--template",
        default="{year}/{month}",
        help="Target path template relative to target dir (default: {year}/{month})",
    )
    mode_group = organize.add_mutually_exclusive_group()
    mode_group.add_argument("--copy", action="store_true", help="Copy files instead of moving")
    mode_group.add_argument("--move", action="store_true", help="Move files instead of copying")
    organize.add_argument(
        "--apply",
        action="store_true",
        help="Apply changes. Without this flag, a dry-run preview is performed.",
    )
    organize.add_argument(
        "--exiftool-path",
        type=Path,
        default=None,
        help="Optional explicit path to exiftool executable",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "organize":
        if not args.source.is_dir():
            parser.error(f"Quellordner existiert nicht oder ist kein Ordner: {args.source}")
        args.target.mkdir(parents=True, exist_ok=True)

        mode = "copy"
        if args.move:
            mode = "move"

        config = SortConfig(
            source_dir=args.source,
            target_dir=args.target,
            target_template=args.template,
            dry_run=not args.apply,
            mode=mode,
            exiftool_path=args.exiftool_path,
        )
        results = organize_media(config)
        print(
            f"Verarbeitet: {results.processed} | Geplant/Ausgeführt: {results.organized} | "
            f"Übersprungen: {results.skipped} | Fehler: {results.errors}"
        )
        return 0 if results.errors == 0 else 1

    parser.error("Unbekannter Befehl")
    return 2
