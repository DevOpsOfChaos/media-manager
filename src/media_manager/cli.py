from __future__ import annotations

import argparse
from pathlib import Path

from media_manager.constants import DEFAULT_TEMPLATE
from media_manager.exiftool import ExifToolClient, ExifToolError, discover_exiftool
from media_manager.sorter import organize


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="media-manager",
        description="Organisiert Bild- und Videodateien anhand von Metadaten.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    organize_parser = subparsers.add_parser(
        "organize",
        help="Sortiert Medien nach Datum in Zielordner.",
    )
    organize_parser.add_argument("source", type=Path, help="Quellordner mit unsortierten Medien")
    organize_parser.add_argument("target", type=Path, help="Zielordner für die sortierten Medien")
    organize_parser.add_argument(
        "--template",
        default=DEFAULT_TEMPLATE,
        help="Ordner-Template, z. B. '{year}/{month_num}-{month_name}/{day}'",
    )
    organize_parser.add_argument(
        "--apply",
        action="store_true",
        help="Wendet Änderungen wirklich an. Ohne diesen Schalter bleibt es bei Dry-Run.",
    )
    mode_group = organize_parser.add_mutually_exclusive_group()
    mode_group.add_argument("--copy", action="store_true", help="Dateien kopieren")
    mode_group.add_argument("--move", action="store_true", help="Dateien verschieben")
    organize_parser.add_argument(
        "--exiftool-path",
        default=None,
        help="Optionaler expliziter Pfad zu ExifTool",
    )
    organize_parser.add_argument(
        "--no-filesystem-fallback",
        action="store_true",
        help="Keinen Fallback auf Dateisystem-Zeitstempel verwenden",
    )

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "organize":
        if not args.source.exists() or not args.source.is_dir():
            parser.error(f"Quellordner existiert nicht oder ist kein Ordner: {args.source}")
        args.target.mkdir(parents=True, exist_ok=True)

        action = "move" if args.move else "copy"

        try:
            exiftool_path = discover_exiftool(args.exiftool_path)
            client = ExifToolClient(exiftool_path)
            version = client.get_version()
        except ExifToolError as exc:
            print(f"Fehler: {exc}")
            return 1

        print(f"ExifTool: {exiftool_path} (Version {version})")
        if not args.apply:
            print("Dry-Run aktiv. Es werden keine Dateien verändert.")

        summary = organize(
            source_dir=args.source,
            target_dir=args.target,
            exiftool=client,
            template=args.template,
            action=action,
            apply_changes=args.apply,
            fallback_to_file_time=not args.no_filesystem_fallback,
        )

        print("\nZusammenfassung")
        print(f"  Gefundene Dateien: {summary.total_files}")
        print(f"  Verarbeitet:       {summary.applied_files}")
        print(f"  Nur simuliert:     {summary.skipped_files}")
        print(f"  Ohne Metadatum:    {summary.no_date_files}")
        return 0

    parser.print_help()
    return 1
