from __future__ import annotations

import argparse
import json
from pathlib import Path

from .core.organizer import (
    DEFAULT_ORGANIZE_PATTERN,
    OrganizePlannerOptions,
    build_organize_dry_run,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="media-manager organize",
        description="Build a dry-run organize plan from one or more source folders.",
    )
    parser.add_argument(
        "--source",
        dest="sources",
        action="append",
        type=Path,
        required=True,
        help="Source directory. Repeat the flag to add multiple source folders.",
    )
    parser.add_argument("--target", type=Path, required=True, help="Target directory root.")
    parser.add_argument(
        "--pattern",
        default=DEFAULT_ORGANIZE_PATTERN,
        help=(
            "Relative target directory pattern. "
            "Supported tokens: {year}, {month}, {day}, {year_month}, {year_month_day}, {source_name}."
        ),
    )
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument("--copy", action="store_true", help="Plan copy-oriented organization (default).")
    mode_group.add_argument("--move", action="store_true", help="Plan move-oriented organization.")
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Reserved for later. Organize v1 currently supports dry-run planning only.",
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
        "--show-files",
        action="store_true",
        help="Print one line per planned/scanned file.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print machine-readable JSON output.",
    )
    parser.add_argument(
        "--exiftool-path",
        type=Path,
        default=None,
        help="Optional explicit path to the exiftool executable.",
    )
    return parser


def _build_payload(plan) -> dict[str, object]:
    return {
        "sources": [str(path) for path in plan.options.source_dirs],
        "target_root": str(plan.options.target_root),
        "pattern": plan.options.pattern,
        "operation_mode": plan.options.operation_mode,
        "missing_sources": [str(path) for path in plan.scan_summary.missing_sources],
        "media_file_count": plan.media_file_count,
        "planned_count": plan.planned_count,
        "skipped_count": plan.skipped_count,
        "conflict_count": plan.conflict_count,
        "error_count": plan.error_count,
        "entries": [
            {
                "source_root": str(item.source_root),
                "source_path": str(item.source_path),
                "relative_source_path": item.scanned_file.relative_path.as_posix(),
                "status": item.status,
                "reason": item.reason,
                "operation_mode": item.operation_mode,
                "target_relative_dir": item.target_relative_dir.as_posix() if item.target_relative_dir else None,
                "target_path": str(item.target_path) if item.target_path else None,
                "resolved_value": item.resolution.resolved_value if item.resolution else None,
                "source_kind": item.resolution.source_kind if item.resolution else None,
                "source_label": item.resolution.source_label if item.resolution else None,
                "confidence": item.resolution.confidence if item.resolution else None,
            }
            for item in plan.entries
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.apply:
        parser.error("Organize apply mode is not implemented yet. Run the command without --apply for dry-run planning.")

    operation_mode = "move" if args.move else "copy"
    plan = build_organize_dry_run(
        OrganizePlannerOptions(
            source_dirs=tuple(args.sources),
            target_root=args.target,
            pattern=args.pattern,
            recursive=not args.non_recursive,
            include_hidden=args.include_hidden,
            operation_mode=operation_mode,
            exiftool_path=args.exiftool_path,
        )
    )

    if args.json:
        print(json.dumps(_build_payload(plan), indent=2, ensure_ascii=False))
        return 0 if plan.error_count == 0 and plan.missing_source_count == 0 else 1

    print("Organize dry run")
    print(f"  Sources: {len(plan.options.source_dirs)}")
    print(f"  Missing sources: {plan.missing_source_count}")
    print(f"  Media files scanned: {plan.media_file_count}")
    print(f"  Planned: {plan.planned_count}")
    print(f"  Skipped: {plan.skipped_count}")
    print(f"  Conflicts: {plan.conflict_count}")
    print(f"  Errors: {plan.error_count}")

    if plan.scan_summary.missing_sources:
        print("\nMissing sources:")
        for path in plan.scan_summary.missing_sources:
            print(f"  - {path}")

    if args.show_files:
        print("\nEntries:")
        for item in plan.entries:
            target_text = str(item.target_path) if item.target_path else "-"
            resolved_text = item.resolution.resolved_value if item.resolution else "-"
            print(
                f"  - [{item.status}] {item.source_path} -> {target_text} | "
                f"date={resolved_text} | reason={item.reason}"
            )

    return 0 if plan.error_count == 0 and plan.missing_source_count == 0 else 1
