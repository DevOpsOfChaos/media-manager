
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .core.state import write_command_run_log
from .core.workflows import (
    DEFAULT_CLEANUP_RENAME_TEMPLATE,
    CleanupWorkflowOptions,
    build_cleanup_dry_run,
)
from .core.organizer import DEFAULT_ORGANIZE_PATTERN


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="media-manager cleanup",
        description="Build a multi-step cleanup dry-run across duplicates, organize, and rename planning.",
    )
    parser.add_argument(
        "--source",
        dest="sources",
        action="append",
        type=Path,
        required=True,
        help="Source directory. Repeat the flag to add multiple source folders.",
    )
    parser.add_argument("--target", type=Path, required=True, help="Target root used for organize planning.")
    parser.add_argument(
        "--organize-pattern",
        default=DEFAULT_ORGANIZE_PATTERN,
        help="Relative organize pattern used for the organize plan.",
    )
    parser.add_argument(
        "--rename-template",
        default=DEFAULT_CLEANUP_RENAME_TEMPLATE,
        help="Rename template used for the rename plan.",
    )
    parser.add_argument(
        "--duplicate-policy",
        choices=["first", "newest", "oldest"],
        help="Optional keep-policy for exact duplicate decision planning.",
    )
    parser.add_argument(
        "--duplicate-mode",
        choices=["copy", "move", "delete"],
        default="copy",
        help="Interpret duplicate planning for copy, move, or delete workflows.",
    )
    parser.add_argument("--non-recursive", action="store_true", help="Only scan the top level of each source folder.")
    parser.add_argument("--include-hidden", action="store_true", help="Include hidden files and folders.")
    parser.add_argument("--show-files", action="store_true", help="Print detail rows for the three plan sections.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")
    parser.add_argument("--run-log", type=Path, help="Optional JSON run-log output path.")
    parser.add_argument(
        "--exiftool-path",
        type=Path,
        default=None,
        help="Optional explicit path to the exiftool executable.",
    )
    return parser


def _build_payload(dry_run) -> dict[str, object]:
    return {
        "sources": [str(path) for path in dry_run.options.source_dirs],
        "target_root": str(dry_run.options.target_root),
        "organize_pattern": dry_run.options.organize_pattern,
        "rename_template": dry_run.options.rename_template,
        "duplicate_policy": dry_run.options.duplicate_policy,
        "duplicate_mode": dry_run.options.duplicate_mode,
        "missing_source_count": dry_run.missing_source_count,
        "media_file_count": dry_run.media_file_count,
        "duplicates": {
            "scanned_files": dry_run.duplicate_scan.scanned_files,
            "exact_groups": len(dry_run.duplicate_scan.exact_groups),
            "duplicate_files": dry_run.duplicate_scan.exact_duplicate_files,
            "extra_duplicates": dry_run.duplicate_scan.exact_duplicates,
            "decisions": len(dry_run.duplicate_bundle.decisions),
            "resolved_groups": dry_run.duplicate_bundle.cleanup_plan.resolved_groups,
            "unresolved_groups": dry_run.duplicate_bundle.cleanup_plan.unresolved_groups,
            "planned_removals": len(dry_run.duplicate_bundle.cleanup_plan.planned_removals),
            "dry_run_ready": dry_run.duplicate_bundle.dry_run.ready,
            "execution_ready": dry_run.duplicate_bundle.execution_preview.ready,
        },
        "organize": {
            "planned_count": dry_run.organize_plan.planned_count,
            "skipped_count": dry_run.organize_plan.skipped_count,
            "conflict_count": dry_run.organize_plan.conflict_count,
            "error_count": dry_run.organize_plan.error_count,
            "entries": [
                {
                    "source_path": str(item.source_path),
                    "target_path": None if item.target_path is None else str(item.target_path),
                    "status": item.status,
                    "reason": item.reason,
                }
                for item in dry_run.organize_plan.entries
            ],
        },
        "rename": {
            "planned_count": dry_run.rename_plan.planned_count,
            "skipped_count": dry_run.rename_plan.skipped_count,
            "conflict_count": dry_run.rename_plan.conflict_count,
            "error_count": dry_run.rename_plan.error_count,
            "entries": [
                {
                    "source_path": str(item.source_path),
                    "target_path": None if item.target_path is None else str(item.target_path),
                    "status": item.status,
                    "reason": item.reason,
                    "rendered_name": item.rendered_name,
                }
                for item in dry_run.rename_plan.entries
            ],
        },
    }


def _print_plan_rows(title: str, entries, *, include_rendered_name: bool = False) -> None:
    print(f"\n{title}:")
    for item in entries:
        target_text = "-" if item.target_path is None else str(item.target_path)
        line = f"  - [{item.status}] {item.source_path} -> {target_text} | reason={item.reason}"
        if include_rendered_name and getattr(item, "rendered_name", None):
            line += f" | rendered={item.rendered_name}"
        print(line)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    invalid_sources = [path for path in args.sources if not path.is_dir()]
    if invalid_sources:
        parser.error(
            "The following source directories do not exist or are not directories: "
            + ", ".join(str(path) for path in invalid_sources)
        )

    dry_run = build_cleanup_dry_run(
        CleanupWorkflowOptions(
            source_dirs=tuple(args.sources),
            target_root=args.target,
            organize_pattern=args.organize_pattern,
            rename_template=args.rename_template,
            duplicate_policy=args.duplicate_policy,
            duplicate_mode=args.duplicate_mode,
            recursive=not args.non_recursive,
            include_hidden=args.include_hidden,
            exiftool_path=args.exiftool_path,
        )
    )

    exit_code = 0
    has_errors = (
        dry_run.missing_source_count > 0
        or dry_run.organize_plan.error_count > 0
        or dry_run.rename_plan.error_count > 0
        or dry_run.duplicate_scan.errors > 0
    )
    if has_errors:
        exit_code = 1

    payload = _build_payload(dry_run)

    if args.run_log is not None:
        write_command_run_log(
            args.run_log,
            command_name="cleanup",
            apply_requested=False,
            exit_code=exit_code,
            payload=payload,
        )

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return exit_code

    print("Cleanup workflow summary")
    print(f"  Sources: {len(dry_run.options.source_dirs)}")
    print(f"  Missing sources: {dry_run.missing_source_count}")
    print(f"  Media files: {dry_run.media_file_count}")
    print(f"  Duplicate groups: {len(dry_run.duplicate_scan.exact_groups)}")
    print(f"  Duplicate decisions: {len(dry_run.duplicate_bundle.decisions)}")
    print(f"  Organize planned/skipped/conflicts/errors: {dry_run.organize_plan.planned_count}/{dry_run.organize_plan.skipped_count}/{dry_run.organize_plan.conflict_count}/{dry_run.organize_plan.error_count}")
    print(f"  Rename planned/skipped/conflicts/errors: {dry_run.rename_plan.planned_count}/{dry_run.rename_plan.skipped_count}/{dry_run.rename_plan.conflict_count}/{dry_run.rename_plan.error_count}")

    print("\nDuplicate plan")
    print(f"  Resolved groups: {dry_run.duplicate_bundle.cleanup_plan.resolved_groups}")
    print(f"  Unresolved groups: {dry_run.duplicate_bundle.cleanup_plan.unresolved_groups}")
    print(f"  Planned removals: {len(dry_run.duplicate_bundle.cleanup_plan.planned_removals)}")
    print(f"  Execution preview ready: {dry_run.duplicate_bundle.execution_preview.ready}")

    if args.show_files:
        _print_plan_rows("Organize entries", dry_run.organize_plan.entries)
        _print_plan_rows("Rename entries", dry_run.rename_plan.entries, include_rendered_name=True)

    return exit_code
