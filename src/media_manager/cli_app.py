from __future__ import annotations

import argparse
import json
from pathlib import Path

from .core.action_model import build_action_model_from_report
from .core.app_manifest import build_app_manifest, build_ui_state_from_report
from .core.plan_snapshot import build_plan_snapshot_from_report
from .core.app_profiles import (
    build_app_profile_payload,
    build_app_profile_preview,
    load_app_profile,
    render_app_profile_command,
    scan_app_profiles,
    summarize_app_profiles,
    validate_app_profile,
    write_app_profile,
)

PROFILE_COMMAND_CHOICES = ["organize", "rename", "duplicates", "cleanup", "doctor", "people"]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="media-manager app",
        description="Print GUI-facing app metadata and compact UI state from reports.",
    )
    subparsers = parser.add_subparsers(dest="app_command")

    manifest_parser = subparsers.add_parser("manifest", help="Print the GUI capability manifest.")
    manifest_parser.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")

    state_parser = subparsers.add_parser("ui-state", help="Build compact UI state from a report JSON file.")
    state_parser.add_argument("--command", required=True, help="Command name for the report, e.g. organize, duplicates, or people.")
    state_parser.add_argument("--report-json", type=Path, required=True, help="Path to a full report.json payload.")
    state_parser.add_argument("--command-json", type=Path, help="Optional command.json payload from a run artifact folder.")
    state_parser.add_argument("--run-id", help="Optional run artifact ID to include in the UI state.")
    state_parser.add_argument("--out", type=Path, help="Optional output path for the generated ui_state.json.")

    snapshot_parser = subparsers.add_parser("plan-snapshot", help="Build a compact plan/list snapshot from a report JSON file.")
    snapshot_parser.add_argument("--command", required=True, help="Command name for the report, e.g. organize or duplicates.")
    snapshot_parser.add_argument("--report-json", type=Path, required=True, help="Path to a full report.json payload.")
    snapshot_parser.add_argument("--run-id", help="Optional run artifact ID to include in the plan snapshot.")
    snapshot_parser.add_argument("--entry-limit", type=int, default=200, help="Maximum rows to include. Default: 200.")
    snapshot_parser.add_argument("--out", type=Path, help="Optional output path for the generated plan_snapshot.json.")

    action_parser = subparsers.add_parser("action-model", help="Build GUI action metadata from a report JSON file.")
    action_parser.add_argument("--command", required=True, help="Command name for the report, e.g. organize, duplicates, or people.")
    action_parser.add_argument("--report-json", type=Path, required=True, help="Path to a full report.json payload.")
    action_parser.add_argument("--command-json", type=Path, help="Optional command.json payload from a run artifact folder.")
    action_parser.add_argument("--run-id", help="Optional run artifact ID to include in the action model.")
    action_parser.add_argument("--out", type=Path, help="Optional output path for the generated action_model.json.")

    profiles_parser = subparsers.add_parser("profiles", help="Create, list, inspect, and render GUI-friendly app profiles.")
    profiles_subparsers = profiles_parser.add_subparsers(dest="profiles_command")

    profiles_init = profiles_subparsers.add_parser("init", help="Create a starter app profile JSON file.")
    profiles_init.add_argument("--out", type=Path, required=True, help="Output profile JSON path.")
    profiles_init.add_argument("--command", choices=PROFILE_COMMAND_CHOICES, required=True, help="Command the profile should run.")
    profiles_init.add_argument("--profile-id", help="Stable profile ID. Defaults to a slug derived from the title.")
    profiles_init.add_argument("--title", required=True, help="Profile title shown in a future GUI.")
    profiles_init.add_argument("--description", default="", help="Optional profile description.")
    profiles_init.add_argument("--tag", action="append", default=[], help="Optional profile tag. Repeat to add multiple tags.")
    profiles_init.add_argument("--favorite", action="store_true", help="Mark the profile as a dashboard favorite.")
    profiles_init.add_argument("--source", dest="sources", action="append", default=[], help="Starter source path. Repeat for multiple sources.")
    profiles_init.add_argument("--target", help="Starter target path for organize/cleanup profiles.")
    profiles_init.add_argument("--run-dir", help="Starter run artifact root.")
    profiles_init.add_argument("--include-pattern", action="append", default=[], help="Starter include glob pattern.")
    profiles_init.add_argument("--exclude-pattern", action="append", default=[], help="Starter exclude glob pattern.")
    profiles_init.add_argument("--media-kind", action="append", default=[], help="Starter duplicate media kind filter.")
    profiles_init.add_argument("--catalog", help="Starter local people catalog path for people profiles.")
    profiles_init.add_argument("--backend", default="", help="Starter people backend, e.g. auto or dlib.")
    profiles_init.add_argument("--people-mode", default="scan", choices=["scan", "review-bundle", "review-apply"], help="People profile mode. Default: scan.")
    profiles_init.add_argument("--bundle-dir", help="Starter people review bundle output directory.")
    profiles_init.add_argument("--workflow-json", help="Starter people workflow JSON path for review-bundle/review-apply.")
    profiles_init.add_argument("--report-json", help="Starter report JSON path.")
    profiles_init.add_argument("--include-encodings", action="store_true", help="Include sensitive face encodings in people scan profiles.")

    profiles_list = profiles_subparsers.add_parser("list", help="List app profile JSON files from a directory.")
    profiles_list.add_argument("--profile-dir", type=Path, required=True, help="Directory containing app profile JSON files.")
    profiles_list.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")

    profiles_show = profiles_subparsers.add_parser("show", help="Show one app profile.")
    profiles_show.add_argument("path", type=Path, help="Profile JSON path.")
    profiles_show.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")

    profiles_validate = profiles_subparsers.add_parser("validate", help="Validate one app profile.")
    profiles_validate.add_argument("path", type=Path, help="Profile JSON path.")
    profiles_validate.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")

    profiles_render = profiles_subparsers.add_parser("render", help="Render the CLI command represented by an app profile.")
    profiles_render.add_argument("path", type=Path, help="Profile JSON path.")
    profiles_render.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")
    return parser


def _read_json_object(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object in {path}")
    return value


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _print_manifest_text(payload: dict[str, object]) -> None:
    app = payload["application"]
    print("Media Manager app manifest")
    print(f"  Application: {app['name']}")
    print(f"  Schema: {payload['schema_version']}")
    print(f"  Primary entrypoint: {app['primary_entrypoint']}")
    print("\nGUI-ready commands")
    for command in payload.get("commands", []):
        print(f"  - {command['id']}: {command['label']} | risk={command['risk_level']} | mode={command['default_mode']}")
    print("\nRun artifact contract")
    contract = payload["artifact_contract"]
    print(f"  Required files: {', '.join(contract['run_directory_files'])}")
    print(f"  Optional files: {', '.join(contract['optional_files'])}")
    if contract.get("people_review_bundle_files"):
        print(f"  People review bundle files: {', '.join(contract['people_review_bundle_files'])}")


def _profile_init_values(args: argparse.Namespace) -> dict[str, object]:
    values: dict[str, object] = {
        "source_dirs": list(args.sources or []),
        "include_patterns": list(args.include_pattern or []),
        "exclude_patterns": list(args.exclude_pattern or []),
    }
    if args.target:
        values["target_root"] = args.target
    if args.run_dir:
        values["run_dir"] = args.run_dir
    if args.media_kind:
        values["media_kinds"] = list(args.media_kind)
    if args.command == "people":
        values["people_mode"] = args.people_mode
        if args.catalog:
            values["catalog"] = args.catalog
        if args.backend:
            values["backend"] = args.backend
        if args.bundle_dir:
            values["bundle_dir"] = args.bundle_dir
        if args.workflow_json:
            values["workflow_json"] = args.workflow_json
        if args.report_json:
            values["report_json"] = args.report_json
        if args.include_encodings:
            values["include_encodings"] = True
    return {key: value for key, value in values.items() if value not in (None, [], "")}


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    command = args.app_command or "manifest"

    if command == "manifest":
        payload = build_app_manifest()
        if args.json:
            print(json.dumps(payload, indent=2, ensure_ascii=False))
        else:
            _print_manifest_text(payload)
        return 0

    if command == "ui-state":
        try:
            report_payload = _read_json_object(args.report_json)
            command_payload = _read_json_object(args.command_json) if args.command_json is not None else None
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            parser.error(str(exc))
        payload = build_ui_state_from_report(
            command_name=args.command,
            report_payload=report_payload,
            command_payload=command_payload,
            run_id=args.run_id,
        )
        if args.out is not None:
            _write_json(args.out, payload)
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0

    if command == "plan-snapshot":
        try:
            report_payload = _read_json_object(args.report_json)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            parser.error(str(exc))
        payload = build_plan_snapshot_from_report(
            command_name=args.command,
            report_payload=report_payload,
            run_id=args.run_id,
            entry_limit=args.entry_limit,
        )
        if args.out is not None:
            _write_json(args.out, payload)
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0

    if command == "action-model":
        try:
            report_payload = _read_json_object(args.report_json)
            command_payload = _read_json_object(args.command_json) if args.command_json is not None else None
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            parser.error(str(exc))
        payload = build_action_model_from_report(
            command_name=args.command,
            report_payload=report_payload,
            command_payload=command_payload,
            run_id=args.run_id,
        )
        if args.out is not None:
            _write_json(args.out, payload)
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0

    if command == "profiles":
        profiles_command = args.profiles_command or "list"
        if profiles_command == "init":
            profile = build_app_profile_payload(
                profile_id=args.profile_id or args.title,
                title=args.title,
                command=args.command,
                description=args.description,
                tags=args.tag or (),
                favorite=args.favorite,
                values=_profile_init_values(args),
            )
            write_app_profile(args.out, profile)
            payload = build_app_profile_preview(profile)
            print(json.dumps(payload, indent=2, ensure_ascii=False))
            return 0 if payload["valid"] else 1

        if profiles_command == "list":
            records = scan_app_profiles(args.profile_dir)
            payload = {
                "profile_dir": str(args.profile_dir),
                "summary": summarize_app_profiles(records),
                "profiles": [item.to_dict() for item in records],
            }
            if args.json:
                print(json.dumps(payload, indent=2, ensure_ascii=False))
            else:
                print("App profiles")
                print(f"  Directory: {args.profile_dir}")
                print(f"  Profiles: {payload['summary']['profile_count']}")
                for item in records:
                    marker = "*" if item.favorite else "-"
                    status = "valid" if item.valid else "invalid"
                    print(f"  {marker} {item.profile_id} | {item.command or '-'} | {status} | {item.title}")
            return 0

        try:
            profile = load_app_profile(args.path)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            parser.error(str(exc))

        if profiles_command == "show":
            payload = build_app_profile_preview(profile)
            if args.json:
                print(json.dumps(payload, indent=2, ensure_ascii=False))
            else:
                print("App profile")
                print(f"  ID: {payload['profile_id']}")
                print(f"  Title: {payload['title']}")
                print(f"  Command: {payload['command']}")
                print(f"  Valid: {payload['valid']}")
                if payload.get("command_preview"):
                    print(f"  Command preview: {payload['command_preview']}")
            return 0 if payload["valid"] else 1

        if profiles_command == "validate":
            validation = validate_app_profile(profile)
            payload = {
                "profile_id": validation.profile_id,
                "command": validation.command,
                "valid": validation.valid,
                "problems": list(validation.problems),
                "warnings": list(validation.warnings),
                "command_argv": list(validation.command_argv),
                "command_preview": validation.command_preview,
            }
            if args.json:
                print(json.dumps(payload, indent=2, ensure_ascii=False))
            else:
                print("App profile validation")
                print(f"  ID: {payload['profile_id']}")
                print(f"  Valid: {payload['valid']}")
                for problem in payload["problems"]:
                    print(f"  Problem: {problem}")
                for warning in payload["warnings"]:
                    print(f"  Warning: {warning}")
            return 0 if validation.valid else 1

        if profiles_command == "render":
            validation = validate_app_profile(profile)
            payload = {
                "profile_id": validation.profile_id,
                "command": validation.command,
                "valid": validation.valid,
                "command_argv": list(validation.command_argv),
                "command_preview": validation.command_preview,
                "problems": list(validation.problems),
                "warnings": list(validation.warnings),
            }
            if args.json:
                print(json.dumps(payload, indent=2, ensure_ascii=False))
            else:
                if validation.command_preview:
                    print(validation.command_preview)
                else:
                    print("Profile is not renderable.")
                    for problem in validation.problems:
                        print(f"  - {problem}")
            return 0 if validation.valid else 1

        parser.error(f"Unsupported profiles command: {profiles_command}")

    parser.error(f"Unsupported app command: {command}")
    return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
