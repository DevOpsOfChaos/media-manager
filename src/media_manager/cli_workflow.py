from __future__ import annotations

import argparse
import json
from pathlib import Path

from . import cli_duplicates, cli_organize, cli_rename, cli_trip

try:  # optional while older cumulative states are still present
    from . import cli_cleanup
except Exception:  # pragma: no cover - compatibility fallback
    cli_cleanup = None

from .core.state import build_history_summary, find_latest_history_entry, scan_history_directory
from .core.workflows import (
    build_workflow_profile_argv,
    build_workflow_wizard_result,
    get_workflow_definition,
    get_workflow_preset,
    get_workflow_problem,
    list_workflow_presets,
    list_workflow_problems,
    list_workflows,
    load_workflow_profile,
    render_workflow_preset_command,
    render_workflow_profile_command,
    save_workflow_profile,
    validate_workflow_profile,
)


def _build_delegate_handlers() -> dict[str, object]:
    handlers = {
        "duplicates": cli_duplicates.main,
        "organize": cli_organize.main,
        "rename": cli_rename.main,
        "trip": cli_trip.main,
    }
    if cli_cleanup is not None:
        handlers["cleanup"] = cli_cleanup.main
    return handlers


DELEGATE_HANDLERS = _build_delegate_handlers()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="media-manager workflow",
        description="Guided CLI entry point for available media-manager workflows.",
    )
    subparsers = parser.add_subparsers(dest="workflow_command")

    list_parser = subparsers.add_parser("list", help="List available workflows.")
    list_parser.add_argument("--json", action="store_true", help="Print JSON output.")

    show_parser = subparsers.add_parser("show", help="Describe one workflow.")
    show_parser.add_argument("name", help="Workflow name.")
    show_parser.add_argument("--json", action="store_true", help="Print JSON output.")

    problems_parser = subparsers.add_parser("problems", help="List common workflow problems.")
    problems_parser.add_argument("--json", action="store_true", help="Print JSON output.")

    recommend_parser = subparsers.add_parser("recommend", help="Recommend a workflow for a common problem.")
    recommend_parser.add_argument("problem", help="Problem slug.")
    recommend_parser.add_argument("--json", action="store_true", help="Print JSON output.")

    wizard_parser = subparsers.add_parser("wizard", help="Build a guided workflow suggestion from a few answers.")
    wizard_parser.add_argument("--problem", help="Optional known problem slug.")
    wizard_parser.add_argument("--source-count", type=int, default=1, help="Approximate number of source folders involved.")
    wizard_parser.add_argument("--has-duplicates", action="store_true", help="Indicate that duplicate concerns are part of the problem.")
    wizard_parser.add_argument("--date-range-known", action="store_true", help="Indicate that a reliable trip or event date range is already known.")
    wizard_parser.add_argument("--wants-trip", action="store_true", help="Bias toward a trip or event collection workflow.")
    wizard_parser.add_argument("--wants-rename", action="store_true", help="Indicate that file naming is a primary concern.")
    wizard_parser.add_argument("--wants-organization", action="store_true", help="Indicate that folder structure is a primary concern.")
    wizard_parser.add_argument("--json", action="store_true", help="Print JSON output.")

    history_parser = subparsers.add_parser("history", help="List workflow run logs and execution journals from a directory.")
    history_parser.add_argument("--path", type=Path, required=True, help="Directory to scan for run logs and journals.")
    history_parser.add_argument("--json", action="store_true", help="Print JSON output.")

    last_parser = subparsers.add_parser("last", help="Show the newest matching workflow history entry.")
    last_parser.add_argument("--path", type=Path, required=True, help="Directory to scan for run logs and journals.")
    last_parser.add_argument("--command", help="Optional command name filter, for example organize or rename.")
    last_parser.add_argument("--json", action="store_true", help="Print JSON output.")

    presets_parser = subparsers.add_parser("presets", help="List built-in workflow presets.")
    presets_parser.add_argument("--json", action="store_true", help="Print JSON output.")

    preset_show_parser = subparsers.add_parser("preset-show", help="Show one built-in workflow preset.")
    preset_show_parser.add_argument("name", help="Preset name.")
    preset_show_parser.add_argument("--json", action="store_true", help="Print JSON output.")

    render_preset_parser = subparsers.add_parser("render-preset", help="Render a command preview from a built-in preset.")
    render_preset_parser.add_argument("name", help="Preset name.")
    _add_preset_override_arguments(render_preset_parser)
    render_preset_parser.add_argument("--json", action="store_true", help="Print JSON output.")

    profile_show_parser = subparsers.add_parser("profile-show", help="Load a workflow profile JSON file and render its command preview.")
    profile_show_parser.add_argument("path", type=Path, help="Path to the workflow profile JSON file.")
    profile_show_parser.add_argument("--json", action="store_true", help="Print JSON output.")

    profile_validate_parser = subparsers.add_parser("profile-validate", help="Validate a workflow profile JSON file.")
    profile_validate_parser.add_argument("path", type=Path, help="Path to the workflow profile JSON file.")
    profile_validate_parser.add_argument("--json", action="store_true", help="Print JSON output.")

    profile_save_parser = subparsers.add_parser("profile-save", help="Create or update a workflow profile JSON file from a preset.")
    profile_save_parser.add_argument("path", type=Path, help="Path where the workflow profile JSON file should be written.")
    profile_save_parser.add_argument("--preset", required=True, help="Preset name.")
    profile_save_parser.add_argument("--profile-name", help="Optional human-readable profile name.")
    profile_save_parser.add_argument("--overwrite", action="store_true", help="Allow overwriting an existing profile JSON file.")
    _add_preset_override_arguments(profile_save_parser)
    profile_save_parser.add_argument("--json", action="store_true", help="Print JSON output.")

    profile_run_parser = subparsers.add_parser("profile-run", help="Run a delegated workflow command from a saved profile.")
    profile_run_parser.add_argument("path", type=Path, help="Path to the workflow profile JSON file.")
    profile_run_parser.add_argument("--show-command", action="store_true", help="Print the rendered workflow command before delegation.")

    run_parser = subparsers.add_parser("run", help="Run a workflow through the shell.")
    run_parser.add_argument("workflow", help="Workflow name to run.")
    run_parser.add_argument("args", nargs=argparse.REMAINDER, help="Arguments forwarded to the delegated workflow.")
    return parser


def _add_preset_override_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--source", dest="sources", action="append", help="Source path. Repeat for multiple sources.")
    parser.add_argument("--target", help="Target path.")
    parser.add_argument("--label", help="Trip label when the preset needs one.")
    parser.add_argument("--start", help="Trip start date in YYYY-MM-DD.")
    parser.add_argument("--end", help="Trip end date in YYYY-MM-DD.")
    parser.add_argument("--pattern", help="Organizer pattern override.")
    parser.add_argument("--template", help="Rename template override.")
    parser.add_argument("--mode", choices=["copy", "move", "delete", "link"], help="Workflow mode override when relevant.")
    parser.add_argument("--policy", choices=["first", "newest", "oldest"], help="Duplicate/similar keep policy override.")
    parser.add_argument("--duplicate-policy", choices=["first", "newest", "oldest"], help="Cleanup duplicate policy override.")
    parser.add_argument("--duplicate-mode", choices=["copy", "move", "delete"], help="Cleanup duplicate mode override.")
    parser.add_argument("--organize-pattern", help="Cleanup organize pattern override.")
    parser.add_argument("--rename-template", help="Cleanup rename template override.")
    parser.add_argument("--show-plan", action="store_true", help="Enable duplicate plan output when the preset supports it.")


def _workflow_payload(item) -> dict[str, str]:
    return {
        "name": item.name,
        "title": item.title,
        "summary": item.summary,
        "best_for": item.best_for,
        "example_command": item.example_command,
        "delegated_command": item.delegated_command,
    }


def _problem_payload(item) -> dict[str, str]:
    return {
        "name": item.name,
        "title": item.title,
        "summary": item.summary,
        "recommended_workflow": item.recommended_workflow,
        "next_step": item.next_step,
    }


def _preset_payload(item) -> dict[str, object]:
    return {
        "name": item.name,
        "title": item.title,
        "summary": item.summary,
        "workflow": item.workflow,
        "required_values": list(item.required_values),
        "default_values": dict(item.default_values),
        "notes": list(item.notes),
    }


def _wizard_payload(result) -> dict[str, object]:
    return {
        "matched_problem": None if result.matched_problem is None else _problem_payload(result.matched_problem),
        "recommended_workflow": _workflow_payload(result.recommended_workflow),
        "confidence": result.confidence,
        "reason": result.reason,
        "notes": list(result.notes),
        "command_suggestions": [
            {"title": item.title, "command": item.command}
            for item in result.command_suggestions
        ],
    }


def _history_payload(item) -> dict[str, object]:
    return {
        "path": str(item.path),
        "record_type": item.record_type,
        "command_name": item.command_name,
        "apply_requested": item.apply_requested,
        "exit_code": item.exit_code,
        "created_at_utc": item.created_at_utc,
        "entry_count": item.entry_count,
        "reversible_entry_count": item.reversible_entry_count,
        "successful": item.successful,
        "has_reversible_entries": item.has_reversible_entries,
    }


def _profile_validation_payload(validation) -> dict[str, object]:
    return {
        "profile_name": validation.profile_name,
        "preset": validation.preset_name,
        "workflow": validation.workflow_name,
        "valid": validation.valid,
        "missing_values": list(validation.missing_values),
        "command": validation.command_preview,
        "problems": list(validation.problems),
    }


def _print_workflow_list(as_json: bool) -> int:
    workflows = [item for item in list_workflows() if item.name in DELEGATE_HANDLERS]
    if as_json:
        print(json.dumps({"workflows": [_workflow_payload(item) for item in workflows]}, indent=2, ensure_ascii=False))
        return 0

    print("Available workflows")
    for item in workflows:
        print(f"  - {item.name}: {item.title}")
        print(f"    {item.summary}")
    return 0


def _print_workflow_show(name: str, as_json: bool) -> int:
    item = get_workflow_definition(name)
    if item is None or item.name not in DELEGATE_HANDLERS:
        print(f"Unknown or unavailable workflow: {name}")
        return 1

    payload = _workflow_payload(item)
    if as_json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0

    print(item.title)
    print(f"  Name: {item.name}")
    print(f"  Summary: {item.summary}")
    print(f"  Best for: {item.best_for}")
    print(f"  Example: {item.example_command}")
    return 0


def _print_problem_list(as_json: bool) -> int:
    problems = list_workflow_problems()
    if as_json:
        print(json.dumps({"problems": [_problem_payload(item) for item in problems]}, indent=2, ensure_ascii=False))
        return 0

    print("Common workflow problems")
    for item in problems:
        print(f"  - {item.name}: {item.title}")
        print(f"    {item.summary}")
    return 0


def _print_recommendation(problem_name: str, as_json: bool) -> int:
    item = get_workflow_problem(problem_name)
    if item is None:
        print(f"Unknown workflow problem: {problem_name}")
        return 1

    workflow = get_workflow_definition(item.recommended_workflow)
    if workflow is None or workflow.name not in DELEGATE_HANDLERS:
        print(f"Recommended workflow is currently unavailable: {item.recommended_workflow}")
        return 1

    payload = {
        "problem": _problem_payload(item),
        "recommended_workflow": _workflow_payload(workflow),
    }
    if as_json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0

    print(item.title)
    print(f"  Problem: {item.summary}")
    print(f"  Recommended workflow: {workflow.name} ({workflow.title})")
    print(f"  Why: {workflow.best_for}")
    print(f"  Next step: {item.next_step}")
    print(f"  Example: {workflow.example_command}")
    return 0


def _print_wizard_result(args: argparse.Namespace) -> int:
    result = build_workflow_wizard_result(
        problem=args.problem,
        source_count=max(1, args.source_count),
        has_duplicates=args.has_duplicates,
        date_range_known=args.date_range_known,
        wants_trip=args.wants_trip,
        wants_rename=args.wants_rename,
        wants_organization=args.wants_organization,
    )
    payload = _wizard_payload(result)
    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0

    print("Workflow wizard suggestion")
    print(f"  Recommended workflow: {result.recommended_workflow.name} ({result.recommended_workflow.title})")
    print(f"  Confidence: {result.confidence}")
    print(f"  Reason: {result.reason}")
    if result.notes:
        print("  Notes:")
        for note in result.notes:
            print(f"    - {note}")
    print("  Suggested commands:")
    for item in result.command_suggestions:
        print(f"    - {item.title}: {item.command}")
    return 0


def _print_history(path: Path, as_json: bool) -> int:
    entries = scan_history_directory(path)
    summary = build_history_summary(entries)
    if as_json:
        print(json.dumps({"summary": summary, "entries": [_history_payload(item) for item in entries]}, indent=2, ensure_ascii=False))
        return 0

    print(f"Workflow history in {path}")
    print(f"  Total entries: {summary['entry_count']}")
    print(f"  Successful: {summary['successful_count']}")
    print(f"  Failed: {summary['failed_count']}")
    print(f"  Reversible entries: {summary['reversible_entry_count']}")
    if summary["latest_created_at_utc"]:
        print(f"  Latest: {summary['latest_created_at_utc']}")
    if not entries:
        print("  No recognized run logs or execution journals found.")
        return 0

    if summary["command_summary"]:
        command_text = ", ".join(f"{key}={value}" for key, value in summary["command_summary"].items())
        print(f"  Commands: {command_text}")
    if summary["record_type_summary"]:
        record_text = ", ".join(f"{key}={value}" for key, value in summary["record_type_summary"].items())
        print(f"  Record types: {record_text}")

    for item in entries:
        print(
            f"  - [{item.record_type}] {item.command_name} | apply={item.apply_requested} | "
            f"exit={item.exit_code} | entries={item.entry_count} | created={item.created_at_utc}"
        )
        print(f"    {item.path}")
    return 0


def _print_last_history(path: Path, command_name: str | None, as_json: bool) -> int:
    entry = find_latest_history_entry(path, command_name=command_name)
    if entry is None:
        if as_json:
            print(json.dumps({"entry": None}, indent=2, ensure_ascii=False))
        else:
            label = f" for command '{command_name}'" if command_name else ""
            print(f"No recognized workflow history entry found{label}.")
        return 1

    payload = _history_payload(entry)
    if as_json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0

    print("Latest workflow history entry")
    print(f"  Type: {entry.record_type}")
    print(f"  Command: {entry.command_name}")
    print(f"  Apply requested: {entry.apply_requested}")
    print(f"  Exit code: {entry.exit_code}")
    print(f"  Entry count: {entry.entry_count}")
    print(f"  Reversible entries: {entry.reversible_entry_count}")
    print(f"  Successful: {entry.successful}")
    print(f"  Has reversible entries: {entry.has_reversible_entries}")
    print(f"  Created: {entry.created_at_utc}")
    print(f"  Path: {entry.path}")
    return 0

# rest unchanged


def _print_presets(as_json: bool) -> int:
    presets = list_workflow_presets()
    if as_json:
        print(json.dumps({"presets": [_preset_payload(item) for item in presets]}, indent=2, ensure_ascii=False))
        return 0

    print("Workflow presets")
    for item in presets:
        print(f"  - {item.name}: {item.title}")
        print(f"    Workflow: {item.workflow}")
        print(f"    {item.summary}")
    return 0


def _print_preset_show(name: str, as_json: bool) -> int:
    preset = get_workflow_preset(name)
    if preset is None:
        print(f"Unknown workflow preset: {name}")
        return 1
    payload = _preset_payload(preset)
    if as_json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0

    print(preset.title)
    print(f"  Name: {preset.name}")
    print(f"  Workflow: {preset.workflow}")
    print(f"  Summary: {preset.summary}")
    print(f"  Required values: {', '.join(preset.required_values)}")
    if preset.default_values:
        print(f"  Default values: {json.dumps(preset.default_values, ensure_ascii=False)}")
    if preset.notes:
        print("  Notes:")
        for note in preset.notes:
            print(f"    - {note}")
    return 0


def _collect_preset_overrides(args: argparse.Namespace) -> dict[str, object]:
    overrides: dict[str, object] = {}
    if getattr(args, "sources", None):
        overrides["source"] = list(args.sources)
    if getattr(args, "target", None):
        overrides["target"] = args.target
    if getattr(args, "label", None):
        overrides["label"] = args.label
    if getattr(args, "start", None):
        overrides["start"] = args.start
    if getattr(args, "end", None):
        overrides["end"] = args.end
    if getattr(args, "pattern", None):
        overrides["pattern"] = args.pattern
    if getattr(args, "template", None):
        overrides["template"] = args.template
    if getattr(args, "mode", None):
        overrides["mode"] = args.mode
    if getattr(args, "policy", None):
        overrides["policy"] = args.policy
    if getattr(args, "duplicate_policy", None):
        overrides["duplicate_policy"] = args.duplicate_policy
    if getattr(args, "duplicate_mode", None):
        overrides["duplicate_mode"] = args.duplicate_mode
    if getattr(args, "organize_pattern", None):
        overrides["organize_pattern"] = args.organize_pattern
    if getattr(args, "rename_template", None):
        overrides["rename_template"] = args.rename_template
    if getattr(args, "show_plan", False):
        overrides["show_plan"] = True
    return overrides


def _print_render_preset(args: argparse.Namespace) -> int:
    try:
        command = render_workflow_preset_command(args.name, overrides=_collect_preset_overrides(args))
    except ValueError as exc:
        print(str(exc))
        return 1

    if args.json:
        print(json.dumps({"preset": args.name, "command": command}, indent=2, ensure_ascii=False))
        return 0

    print(command)
    return 0


def _print_profile_show(path: Path, as_json: bool) -> int:
    try:
        profile = load_workflow_profile(path)
        command = render_workflow_profile_command(profile)
    except Exception as exc:
        print(str(exc))
        return 1

    payload = {
        "profile_name": profile.profile_name,
        "preset": profile.preset_name,
        "values": dict(profile.values),
        "command": command,
    }
    if as_json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0

    print(profile.profile_name)
    print(f"  Preset: {profile.preset_name}")
    print(f"  Command: {command}")
    return 0


def _print_profile_validate(path: Path, as_json: bool) -> int:
    try:
        profile = load_workflow_profile(path)
        validation = validate_workflow_profile(profile)
    except Exception as exc:
        print(str(exc))
        return 1

    payload = _profile_validation_payload(validation)
    if as_json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(validation.profile_name)
        print(f"  Preset: {validation.preset_name}")
        print(f"  Workflow: {validation.workflow_name}")
        print(f"  Valid: {validation.valid}")
        if validation.command_preview:
            print(f"  Command: {validation.command_preview}")
        if validation.missing_values:
            print(f"  Missing values: {', '.join(validation.missing_values)}")
        if validation.problems:
            print("  Problems:")
            for problem in validation.problems:
                print(f"    - {problem}")
    return 0 if validation.valid else 1


def _print_profile_save(args: argparse.Namespace) -> int:
    try:
        profile = save_workflow_profile(
            args.path,
            profile_name=args.profile_name or args.path.stem,
            preset_name=args.preset,
            values=_collect_preset_overrides(args),
            overwrite=args.overwrite,
        )
        command = render_workflow_profile_command(profile)
    except Exception as exc:
        print(str(exc))
        return 1

    payload = {
        "path": str(args.path),
        "profile_name": profile.profile_name,
        "preset": profile.preset_name,
        "values": dict(profile.values),
        "command": command,
    }
    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0

    print(f"Saved workflow profile: {args.path}")
    print(f"  Profile: {profile.profile_name}")
    print(f"  Preset: {profile.preset_name}")
    print(f"  Command: {command}")
    return 0


def _run_workflow_profile(path: Path, show_command: bool) -> int:
    try:
        profile = load_workflow_profile(path)
        validation = validate_workflow_profile(profile)
    except Exception as exc:
        print(str(exc))
        return 1

    if not validation.valid or not validation.command_argv or validation.workflow_name is None:
        if validation.problems:
            for problem in validation.problems:
                print(problem)
        else:
            print("Workflow profile is not valid.")
        return 1

    if show_command and validation.command_preview:
        print(validation.command_preview)

    forwarded_args = list(validation.command_argv[4:])
    return _run_delegated_workflow(validation.workflow_name, forwarded_args)


def _run_delegated_workflow(name: str, forwarded_args: list[str]) -> int:
    normalized = name.strip().lower()
    handler = DELEGATE_HANDLERS.get(normalized)
    if handler is None:
        print(f"Unknown or unavailable workflow: {name}")
        return 1
    return int(handler(forwarded_args))


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.workflow_command is None:
        parser.print_help()
        print(
            "\nTry one of these:\n"
            "  media-manager workflow list\n"
            "  media-manager workflow show cleanup\n"
            "  media-manager workflow problems\n"
            "  media-manager workflow recommend messy-multi-source-library\n"
            "  media-manager workflow wizard --source-count 3 --has-duplicates --wants-organization\n"
            "  media-manager workflow presets\n"
            "  media-manager workflow preset-show cleanup-family-library\n"
            "  media-manager workflow render-preset cleanup-family-library --source <A> --source <B> --target <TARGET>\n"
            "  media-manager workflow profile-save profiles/family-cleanup.json --preset cleanup-family-library --source <A> --source <B> --target <TARGET>\n"
            "  media-manager workflow profile-show <PROFILE.json>\n"
            "  media-manager workflow profile-validate <PROFILE.json>\n"
            "  media-manager workflow profile-run <PROFILE.json> --show-command\n"
            "  media-manager workflow history --path <RUNS_DIR>\n"
            "  media-manager workflow last --path <RUNS_DIR> --command organize\n"
            "  media-manager workflow run cleanup --source <A> --source <B> --target <TARGET>\n"
        )
        return 0

    if args.workflow_command == "list":
        return _print_workflow_list(args.json)
    if args.workflow_command == "show":
        return _print_workflow_show(args.name, args.json)
    if args.workflow_command == "problems":
        return _print_problem_list(args.json)
    if args.workflow_command == "recommend":
        return _print_recommendation(args.problem, args.json)
    if args.workflow_command == "wizard":
        return _print_wizard_result(args)
    if args.workflow_command == "history":
        return _print_history(args.path, args.json)
    if args.workflow_command == "last":
        return _print_last_history(args.path, args.command, args.json)
    if args.workflow_command == "presets":
        return _print_presets(args.json)
    if args.workflow_command == "preset-show":
        return _print_preset_show(args.name, args.json)
    if args.workflow_command == "render-preset":
        return _print_render_preset(args)
    if args.workflow_command == "profile-show":
        return _print_profile_show(args.path, args.json)
    if args.workflow_command == "profile-validate":
        return _print_profile_validate(args.path, args.json)
    if args.workflow_command == "profile-save":
        return _print_profile_save(args)
    if args.workflow_command == "profile-run":
        return _run_workflow_profile(args.path, args.show_command)
    if args.workflow_command == "run":
        return _run_delegated_workflow(args.workflow, list(args.args))

    parser.print_help()
    return 2
