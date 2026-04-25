from __future__ import annotations

import argparse
import json
from pathlib import Path

from .core.doctor import DoctorOptions, build_doctor_payload, build_doctor_report
from .core.report_export import write_json_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="media-manager doctor",
        description="Validate workflow inputs and report common CLI configuration problems without changing files.",
    )
    parser.add_argument(
        "--command",
        choices=["general", "organize", "rename", "cleanup", "duplicates", "inspect", "trip"],
        default="general",
        help="Workflow context for diagnostics. Default: general.",
    )
    parser.add_argument(
        "--source",
        dest="sources",
        action="append",
        type=Path,
        default=[],
        help="Source directory to validate. Repeat the flag to add multiple source folders.",
    )
    parser.add_argument("--target", type=Path, help="Optional target directory to validate for organize/cleanup workflows.")
    parser.add_argument("--non-recursive", action="store_true", help="Only preview the top level of each source folder.")
    parser.add_argument("--include-hidden", action="store_true", help="Include hidden files and hidden folders in the preview.")
    parser.add_argument("--follow-symlinks", action="store_true", help="Follow symlinked directories while previewing sources.")
    parser.add_argument(
        "--include-pattern",
        action="append",
        default=[],
        help="Only include paths matching this glob-style pattern. Repeat to add multiple include rules.",
    )
    parser.add_argument(
        "--exclude-pattern",
        action="append",
        default=[],
        help="Exclude paths matching this glob-style pattern. Repeat to add multiple exclude rules.",
    )
    parser.add_argument("--report-json", type=Path, help="Optional path where the full diagnostic JSON report is written.")
    parser.add_argument("--run-log", type=Path, help="Optional run-log path to validate as an output file.")
    parser.add_argument("--review-json", type=Path, help="Optional review export path to validate as an output file.")
    parser.add_argument("--journal", type=Path, help="Optional execution journal path to validate as an output file.")
    parser.add_argument("--history-dir", type=Path, help="Optional history directory to validate.")
    parser.add_argument("--exiftool-path", type=Path, help="Optional explicit exiftool path to validate.")
    parser.add_argument(
        "--max-scan-files",
        type=int,
        default=5000,
        help="Maximum number of filesystem entries to inspect per diagnostic run. Default: 5000.",
    )
    parser.add_argument("--fail-on-warnings", action="store_true", help="Return exit code 1 when warnings are found.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")
    return parser


def _print_text_report(payload: dict[str, object]) -> None:
    summary = payload["summary"]
    print("Doctor summary")
    print(f"  Command context: {payload['command']}")
    print(f"  Status: {payload['status']}")
    print(f"  Ready: {payload['ready']}")
    print(f"  Next action: {payload['next_action']}")
    print(f"  Sources: {summary['source_count']}")
    print(f"  Files previewed: {summary['scanned_file_count']}")
    print(f"  Files included by filters: {summary['included_file_count']}")
    print(f"  Errors: {summary['error_count']}")
    print(f"  Warnings: {summary['warning_count']}")
    print(f"  Info: {summary['info_count']}")

    source_previews = payload.get("source_previews", [])
    if source_previews:
        print("\nSource previews")
        for item in source_previews:
            print(
                f"  - {item['source_root']} | included={item['included_file_count']} "
                f"previewed={item['scanned_file_count']} filtered_by_include={item['excluded_by_include_count']} "
                f"filtered_by_exclude={item['excluded_by_exclude_count']}"
            )

    diagnostics = payload.get("diagnostics", [])
    if diagnostics:
        print("\nDiagnostics")
        for item in diagnostics:
            path_text = "" if item.get("path") is None else f" | {item['path']}"
            print(f"  - [{item['severity']}] {item['code']}: {item['message']}{path_text}")
            if item.get("hint"):
                print(f"    hint: {item['hint']}")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    report = build_doctor_report(
        DoctorOptions(
            command=args.command,
            source_dirs=tuple(args.sources or ()),
            target_root=args.target,
            include_patterns=tuple(args.include_pattern or ()),
            exclude_patterns=tuple(args.exclude_pattern or ()),
            report_json_path=args.report_json,
            review_json_path=args.review_json,
            run_log_path=args.run_log,
            journal_path=args.journal,
            history_dir=args.history_dir,
            exiftool_path=args.exiftool_path,
            recursive=not args.non_recursive,
            include_hidden=args.include_hidden,
            follow_symlinks=args.follow_symlinks,
            max_scan_files=args.max_scan_files,
        )
    )
    payload = build_doctor_payload(report)

    if args.report_json is not None:
        write_json_report(args.report_json, payload)

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        _print_text_report(payload)
        if args.report_json is not None:
            print(f"\nWrote diagnostic report: {args.report_json}")

    if report.error_count > 0:
        return 1
    if args.fail_on_warnings and report.warning_count > 0:
        return 1
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
