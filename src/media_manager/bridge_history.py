"""Run history bridge for the Tauri desktop app.

Called by the Rust backend via subprocess:
    python -m media_manager.bridge_history list
    python -m media_manager.bridge_history get <run_id>

Output: JSON on stdout. Errors: JSON on stderr.

Run directory:
    Default: ~/.media-manager/runs/
    Override: --run-dir CLI argument
    Override: MEDIA_MANAGER_RUNS_PATH env variable
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from media_manager.core.run_index import (
    build_run_artifacts_payload,
    find_run_artifact,
    list_run_artifacts,
    load_run_artifact_payload,
)

DEFAULT_RUNS_PATH = Path.home() / ".media-manager" / "runs"


def _resolve_runs_path(cli_path: str | None = None) -> Path:
    if cli_path:
        return Path(cli_path)
    env_path = os.environ.get("MEDIA_MANAGER_RUNS_PATH")
    if env_path:
        return Path(env_path)
    return DEFAULT_RUNS_PATH


def _emit(payload: dict) -> None:
    print(json.dumps(payload, indent=2, ensure_ascii=False))


def _fail(message: str, exit_code: int = 1) -> int:
    print(json.dumps({"error": message}), file=sys.stderr)
    return exit_code


def cmd_list(runs_path: Path, limit: int) -> int:
    if not runs_path.exists():
        _emit({"root_dir": str(runs_path), "run_count": 0, "valid_count": 0, "invalid_count": 0, "runs": []})
        return 0
    records = list_run_artifacts(runs_path, limit=limit)
    payload = build_run_artifacts_payload(records, root_dir=runs_path)
    _emit(dict(payload))
    return 0


def cmd_get(runs_path: Path, run_id: str) -> int:
    record = find_run_artifact(runs_path, run_id)
    if record is None:
        return _fail(f"Run not found: {run_id}", exit_code=1)

    detail: dict = {
        "run_id": record.run_dir.name,
        "run_dir": str(record.run_dir),
        "command": record.command,
        "mode": record.mode,
        "created_at_utc": record.created_at_utc,
        "exit_code": record.exit_code,
        "status": record.status,
        "next_action": record.next_action,
        "review_candidate_count": record.review_candidate_count,
        "has_ui_state": record.has_ui_state,
        "has_plan_snapshot": record.has_plan_snapshot,
        "has_action_model": record.has_action_model,
        "action_count": record.action_count,
        "recommended_action_count": record.recommended_action_count,
        "has_journal": record.has_journal,
        "valid": record.valid,
        "missing_files": list(record.missing_files),
        "errors": list(record.errors),
    }

    # Load summary text
    summary_path = record.run_dir / "summary.txt"
    if summary_path.is_file():
        try:
            detail["summary"] = summary_path.read_text(encoding="utf-8")
        except OSError:
            detail["summary"] = None
    else:
        detail["summary"] = None

    # Load command.json
    command_path = record.run_dir / "command.json"
    if command_path.is_file():
        try:
            detail["command_json"] = json.loads(command_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            detail["command_json"] = None
    else:
        detail["command_json"] = None

    # Load report.json outcome
    report_path = record.run_dir / "report.json"
    if report_path.is_file():
        try:
            report = json.loads(report_path.read_text(encoding="utf-8"))
            detail["report_outcome"] = report.get("outcome_report") if isinstance(report, dict) else None
        except (OSError, json.JSONDecodeError):
            detail["report_outcome"] = None
    else:
        detail["report_outcome"] = None

    _emit(detail)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="media_manager.bridge_history",
        description="Run history bridge for Tauri desktop app.",
    )
    parser.add_argument(
        "action",
        choices=["list", "get"],
        help="Operation to perform.",
    )
    parser.add_argument(
        "run_id",
        nargs="?",
        default=None,
        help="Run ID for get action.",
    )
    parser.add_argument(
        "--run-dir",
        dest="runs_path",
        default=None,
        help="Override the runs directory.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=50,
        help="Max runs for list. Default: 50.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv if argv is not None else sys.argv[1:])

    runs_path = _resolve_runs_path(args.runs_path)

    if args.action == "list":
        return cmd_list(runs_path, args.limit)

    if args.action == "get":
        if not args.run_id:
            return _fail("run_id required for get action", exit_code=2)
        return cmd_get(runs_path, args.run_id)

    return _fail(f"Unknown action: {args.action}", exit_code=2)


if __name__ == "__main__":
    raise SystemExit(main())
