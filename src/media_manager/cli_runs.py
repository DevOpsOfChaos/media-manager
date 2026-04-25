from __future__ import annotations

import argparse
import json
from pathlib import Path

from .core.run_index import (
    build_run_artifacts_payload,
    find_run_artifact,
    list_run_artifacts,
    load_run_artifact_payload,
    validate_run_artifacts,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="media-manager runs",
        description="List, inspect, and validate structured run artifact directories.",
    )
    parser.add_argument(
        "--run-dir",
        type=Path,
        default=Path("runs"),
        help="Root directory containing run artifact folders. Default: ./runs.",
    )
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")

    subparsers = parser.add_subparsers(dest="runs_command")
    list_parser = subparsers.add_parser("list", help="List recent run artifact folders.")
    list_parser.add_argument("--limit", type=int, default=20, help="Maximum number of runs to show. Default: 20.")

    show_parser = subparsers.add_parser("show", help="Show one run artifact folder.")
    show_parser.add_argument("run_id", help="Run folder name or unique prefix.")
    show_parser.add_argument(
        "--artifact",
        choices=["summary", "command", "report", "review", "ui-state", "plan-snapshot", "action-model", "journal"],
        default="summary",
        help="Artifact to print. Default: summary.",
    )

    validate_parser = subparsers.add_parser("validate", help="Validate run artifact folders.")
    validate_parser.add_argument("--limit", type=int, default=None, help="Optional maximum number of runs to validate.")
    return parser


def _print_runs_table(payload: dict[str, object]) -> None:
    print("Run artifacts")
    print(f"  Root: {payload['root_dir']}")
    print(f"  Runs: {payload['run_count']}")
    print(f"  Invalid: {payload['invalid_count']}")
    runs = payload.get("runs", [])
    if not runs:
        return
    print("\nRecent runs")
    for row in runs:
        marker = "OK" if row.get("valid") else "BROKEN"
        print(
            f"  - [{marker}] {row.get('run_id')} | {row.get('command')} | {row.get('mode')} | "
            f"status={row.get('status')} review={row.get('review_candidate_count')} "
            f"actions={row.get('recommended_action_count')}/{row.get('action_count')} exit={row.get('exit_code')}"
        )
        if row.get("next_action"):
            print(f"    next: {row.get('next_action')}")
        if row.get("missing_files"):
            print(f"    missing: {', '.join(row.get('missing_files', []))}")
        if row.get("errors"):
            print(f"    errors: {'; '.join(row.get('errors', []))}")


def _artifact_filename(name: str) -> str:
    if name == "summary":
        return "summary.txt"
    if name == "ui-state":
        return "ui_state.json"
    if name == "plan-snapshot":
        return "plan_snapshot.json"
    if name == "action-model":
        return "action_model.json"
    return f"{name}.json"


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    command = args.runs_command or "list"

    if command == "list":
        records = list_run_artifacts(args.run_dir, limit=args.limit)
        payload = build_run_artifacts_payload(records, root_dir=args.run_dir)
        if args.json:
            print(json.dumps(payload, indent=2, ensure_ascii=False))
        else:
            _print_runs_table(payload)
        return 0

    if command == "validate":
        validation = validate_run_artifacts(args.run_dir, limit=args.limit)
        payload = build_run_artifacts_payload(validation.records, root_dir=args.run_dir)
        payload["errors"] = list(validation.errors)
        payload["ready"] = validation.ready
        if args.json:
            print(json.dumps(payload, indent=2, ensure_ascii=False))
        else:
            _print_runs_table(payload)
            if validation.errors:
                print("\nValidation errors")
                for error in validation.errors:
                    print(f"  - {error}")
        return 0 if validation.ready else 1

    if command == "show":
        record = find_run_artifact(args.run_dir, args.run_id)
        if record is None:
            parser.error(f"No unique run artifact found for: {args.run_id}")
        artifact_filename = _artifact_filename(args.artifact)
        try:
            artifact = load_run_artifact_payload(record.run_dir, artifact_filename)
        except (OSError, ValueError) as exc:
            parser.error(str(exc))
        if isinstance(artifact, str):
            print(artifact, end="" if artifact.endswith("\n") else "\n")
        else:
            print(json.dumps(artifact, indent=2, ensure_ascii=False))
        return 0

    parser.error(f"Unsupported runs command: {command}")
    return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
