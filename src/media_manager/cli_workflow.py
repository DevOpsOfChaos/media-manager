from __future__ import annotations

import argparse
import io
import json
from contextlib import redirect_stdout
from pathlib import Path

from . import cli_duplicates, cli_organize, cli_rename, cli_trip

try:  # optional while older cumulative states are still present
    from . import cli_cleanup
except Exception:  # pragma: no cover - compatibility fallback
    cli_cleanup = None

from .core.state import build_history_summary, find_latest_history_entry, scan_history_directory
from .core.workflows import (
    build_workflow_profile_inventory,
    build_workflow_profile_argv,
    build_workflow_wizard_result,
    compare_workflow_profile_bundles,
    build_workflow_profile_bundle_inventory,
    extract_workflow_profile_bundle,
    filter_workflow_profile_bundle,
    sync_workflow_profile_bundle,
    get_workflow_definition,
    get_workflow_preset,
    get_workflow_problem,
    list_workflow_presets,
    list_workflow_problems,
    list_workflows,
    load_workflow_profile,
    load_workflow_profile_bundle,
    merge_workflow_profile_bundles,
    render_workflow_preset_command,
    render_workflow_profile_command,
    save_workflow_profile,
    validate_workflow_profile,
    write_workflow_profile_bundle,
    WorkflowProfile,
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
    history_parser.add_argument("--command", help="Optional command name filter, for example organize or rename.")
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

    profile_list_parser = subparsers.add_parser("profile-list", help="List and summarize saved workflow profiles from a directory.")
    _add_profile_directory_arguments(profile_list_parser)
    profile_list_parser.add_argument("--json", action="store_true", help="Print JSON output.")

    profile_audit_parser = subparsers.add_parser("profile-audit", help="Validate all saved workflow profiles in a directory.")
    _add_profile_directory_arguments(profile_audit_parser)
    profile_audit_parser.add_argument("--fail-on-empty", action="store_true", help="Return exit code 1 when no matching profiles are found.")
    profile_audit_parser.add_argument("--json", action="store_true", help="Print JSON output.")

    profile_bundle_write_parser = subparsers.add_parser("profile-bundle-write", help="Export workflow profiles from a directory into a bundle JSON file.")
    profile_bundle_write_parser.add_argument("output_path", type=Path, help="Path where the workflow profile bundle JSON file should be written.")
    _add_profile_directory_arguments(profile_bundle_write_parser)
    profile_bundle_write_parser.add_argument("--json", action="store_true", help="Print JSON output.")

    profile_bundle_show_parser = subparsers.add_parser("profile-bundle-show", help="Inspect a workflow profile bundle JSON file.")
    profile_bundle_show_parser.add_argument("path", type=Path, help="Path to the workflow profile bundle JSON file.")
    _add_profile_bundle_arguments(profile_bundle_show_parser)
    profile_bundle_show_parser.add_argument("--json", action="store_true", help="Print JSON output.")

    profile_bundle_audit_parser = subparsers.add_parser("profile-bundle-audit", help="Audit a workflow profile bundle JSON file for invalid profiles.")
    profile_bundle_audit_parser.add_argument("path", type=Path, help="Path to the workflow profile bundle JSON file.")
    _add_profile_bundle_arguments(profile_bundle_audit_parser)
    profile_bundle_audit_parser.add_argument("--fail-on-empty", action="store_true", help="Return exit code 1 when no matching profiles are found.")
    profile_bundle_audit_parser.add_argument("--json", action="store_true", help="Print JSON output.")

    profile_bundle_extract_parser = subparsers.add_parser("profile-bundle-extract", help="Extract workflow profile JSON files from a bundle into a target directory.")
    profile_bundle_extract_parser.add_argument("path", type=Path, help="Path to the workflow profile bundle JSON file.")
    profile_bundle_extract_parser.add_argument("--target-dir", type=Path, required=True, help="Directory where matching workflow profile JSON files should be written.")
    _add_profile_bundle_arguments(profile_bundle_extract_parser, include_show_command=False, include_summary_only=False)
    profile_bundle_extract_parser.add_argument("--overwrite", action="store_true", help="Allow overwriting existing profile JSON files when their content differs.")
    profile_bundle_extract_parser.add_argument("--flatten", action="store_true", help="Write matching profiles directly into the target directory instead of preserving their relative bundle paths.")
    profile_bundle_extract_parser.add_argument("--fail-on-empty", action="store_true", help="Return exit code 1 when no matching bundle profiles are found.")
    profile_bundle_extract_parser.add_argument("--json", action="store_true", help="Print JSON output.")

    profile_bundle_sync_parser = subparsers.add_parser("profile-bundle-sync", help="Preview or apply a workflow profile bundle against a target directory.")
    profile_bundle_sync_parser.add_argument("path", type=Path, help="Path to the workflow profile bundle JSON file.")
    profile_bundle_sync_parser.add_argument("--target-dir", type=Path, required=True, help="Directory that should receive the selected bundle profiles.")
    _add_profile_bundle_arguments(profile_bundle_sync_parser)
    profile_bundle_sync_parser.add_argument("--overwrite", action="store_true", help="Allow overwriting existing profile JSON files when their content differs.")
    profile_bundle_sync_parser.add_argument("--prune", action="store_true", help="Remove existing target JSON profiles that are not present in the selected bundle set.")
    profile_bundle_sync_parser.add_argument("--flatten", action="store_true", help="Write selected profiles directly into the target directory instead of preserving relative bundle paths.")
    profile_bundle_sync_parser.add_argument("--apply", action="store_true", help="Execute the planned bundle sync actions instead of only previewing them.")
    profile_bundle_sync_parser.add_argument("--fail-on-empty", action="store_true", help="Return exit code 1 when no matching bundle profiles are found.")
    profile_bundle_sync_parser.add_argument("--json", action="store_true", help="Print JSON output.")

    profile_bundle_merge_parser = subparsers.add_parser("profile-bundle-merge", help="Merge multiple workflow profile bundle JSON files into one bundle.")
    profile_bundle_merge_parser.add_argument("output_path", type=Path, help="Path where the merged workflow profile bundle JSON file should be written.")
    profile_bundle_merge_parser.add_argument("bundle_paths", nargs="+", type=Path, help="Input workflow profile bundle JSON files.")
    _add_profile_bundle_arguments(profile_bundle_merge_parser, include_show_command=False, include_summary_only=False)
    profile_bundle_merge_parser.add_argument("--prefer", choices=["first", "last"], default="last", help="When the same relative profile path exists multiple times, keep the first or last occurrence. Default: last.")
    profile_bundle_merge_parser.add_argument("--json", action="store_true", help="Print JSON output.")

    profile_bundle_compare_parser = subparsers.add_parser("profile-bundle-compare", help="Compare two workflow profile bundle JSON files.")
    profile_bundle_compare_parser.add_argument("left_path", type=Path, help="Left workflow profile bundle JSON file.")
    profile_bundle_compare_parser.add_argument("right_path", type=Path, help="Right workflow profile bundle JSON file.")
    _add_profile_bundle_arguments(profile_bundle_compare_parser)
    profile_bundle_compare_parser.add_argument("--only-added", action="store_true", help="Only include added comparison entries.")
    profile_bundle_compare_parser.add_argument("--only-removed", action="store_true", help="Only include removed comparison entries.")
    profile_bundle_compare_parser.add_argument("--only-changed", action="store_true", help="Only include changed comparison entries.")
    profile_bundle_compare_parser.add_argument("--only-unchanged", action="store_true", help="Only include unchanged comparison entries.")
    profile_bundle_compare_parser.add_argument("--fail-on-changes", action="store_true", help="Return exit code 1 when matching bundle entries changed, were added, or were removed.")
    profile_bundle_compare_parser.add_argument("--fail-on-empty", action="store_true", help="Return exit code 1 when no matching comparison entries are found.")
    profile_bundle_compare_parser.add_argument("--json", action="store_true", help="Print JSON output.")

    profile_bundle_run_parser = subparsers.add_parser("profile-bundle-run", help="Run all matching valid workflow profiles from a bundle JSON file.")
    profile_bundle_run_parser.add_argument("path", type=Path, help="Path to the workflow profile bundle JSON file.")
    _add_profile_bundle_arguments(profile_bundle_run_parser, include_summary_only=False)
    profile_bundle_run_parser.add_argument("--continue-on-error", action="store_true", help="Keep running later matching bundle profiles even if one delegated workflow returns a non-zero exit code.")
    profile_bundle_run_parser.add_argument("--fail-on-empty", action="store_true", help="Return exit code 1 when no matching bundle profiles are found.")
    profile_bundle_run_parser.add_argument("--json", action="store_true", help="Print JSON output.")

    profile_bundle_list_dir_parser = subparsers.add_parser("profile-bundle-list-dir", help="List and summarize workflow profile bundle JSON files from a directory.")
    _add_profile_bundle_directory_arguments(profile_bundle_list_dir_parser)
    profile_bundle_list_dir_parser.add_argument("--json", action="store_true", help="Print JSON output.")

    profile_bundle_audit_dir_parser = subparsers.add_parser("profile-bundle-audit-dir", help="Audit workflow profile bundle JSON files from a directory.")
    _add_profile_bundle_directory_arguments(profile_bundle_audit_dir_parser)
    profile_bundle_audit_dir_parser.add_argument("--fail-on-empty", action="store_true", help="Return exit code 1 when no matching bundles are found.")
    profile_bundle_audit_dir_parser.add_argument("--json", action="store_true", help="Print JSON output.")

    profile_bundle_run_dir_parser = subparsers.add_parser("profile-bundle-run-dir", help="Run all matching valid workflow profiles from bundle JSON files in a directory.")
    _add_profile_bundle_directory_arguments(profile_bundle_run_dir_parser, include_summary_only=False)
    profile_bundle_run_dir_parser.add_argument("--continue-on-error", action="store_true", help="Keep running later matching bundles after one delegated workflow returns a non-zero exit code.")
    profile_bundle_run_dir_parser.add_argument("--fail-on-empty", action="store_true", help="Return exit code 1 when no matching bundles are found.")
    profile_bundle_run_dir_parser.add_argument("--json", action="store_true", help="Print JSON output.")

    profile_run_dir_parser = subparsers.add_parser("profile-run-dir", help="Run all matching valid workflow profiles from a directory.")
    _add_profile_directory_arguments(profile_run_dir_parser, include_summary_only=False)
    profile_run_dir_parser.add_argument("--continue-on-error", action="store_true", help="Keep running later matching profiles after one delegated workflow returns a non-zero exit code.")
    profile_run_dir_parser.add_argument("--fail-on-empty", action="store_true", help="Return exit code 1 when no matching profiles are found.")
    profile_run_dir_parser.add_argument("--json", action="store_true", help="Print JSON output.")

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


def _add_profile_directory_arguments(
    parser: argparse.ArgumentParser,
    *,
    include_show_command: bool = True,
    include_summary_only: bool = True,
) -> None:
    parser.add_argument("--profiles-dir", type=Path, required=True, help="Directory containing workflow profile JSON files.")
    parser.add_argument("--workflow", help="Optional workflow filter, for example cleanup or trip.")
    parser.add_argument("--preset", help="Optional preset filter, for example cleanup-family-library.")
    parser.add_argument("--only-valid", action="store_true", help="Only include valid profiles.")
    parser.add_argument("--only-invalid", action="store_true", help="Only include invalid profiles.")
    if include_show_command:
        parser.add_argument("--show-command", action="store_true", help="Include rendered command previews in text output.")
    if include_summary_only:
        parser.add_argument("--summary-only", action="store_true", help="Only print or return the summary block.")


def _add_profile_bundle_arguments(
    parser: argparse.ArgumentParser,
    *,
    include_show_command: bool = True,
    include_summary_only: bool = True,
) -> None:
    parser.add_argument("--workflow", help="Optional workflow filter, for example cleanup or trip.")
    parser.add_argument("--preset", help="Optional preset filter, for example cleanup-family-library.")
    parser.add_argument("--only-valid", action="store_true", help="Only include valid profiles.")
    parser.add_argument("--only-invalid", action="store_true", help="Only include invalid profiles.")
    if include_show_command:
        parser.add_argument("--show-command", action="store_true", help="Include rendered command previews in text output.")
    if include_summary_only:
        parser.add_argument("--summary-only", action="store_true", help="Only print or return the summary block.")


def _add_profile_bundle_directory_arguments(
    parser: argparse.ArgumentParser,
    *,
    include_show_command: bool = True,
    include_summary_only: bool = True,
) -> None:
    parser.add_argument("--bundles-dir", type=Path, required=True, help="Directory containing workflow profile bundle JSON files.")
    parser.add_argument("--bundle-name", help="Optional bundle name filter based on the bundle file stem.")
    parser.add_argument("--workflow", help="Optional workflow filter, for example cleanup or trip.")
    parser.add_argument("--preset", help="Optional preset filter, for example cleanup-family-library.")
    parser.add_argument("--only-valid", action="store_true", help="Only include valid profiles inside each matching bundle.")
    parser.add_argument("--only-invalid", action="store_true", help="Only include invalid profiles inside each matching bundle.")
    parser.add_argument("--only-clean-bundles", action="store_true", help="Only include bundles whose selected profiles are all valid.")
    parser.add_argument("--only-problematic-bundles", action="store_true", help="Only include bundles that are unreadable or contain invalid selected profiles.")
    if include_show_command:
        parser.add_argument("--show-command", action="store_true", help="Include rendered command previews in text output.")
    if include_summary_only:
        parser.add_argument("--summary-only", action="store_true", help="Only print or return the summary block.")


def _load_filtered_bundle_for_record(record, args):
    bundle = load_workflow_profile_bundle(record.bundle_path)
    return filter_workflow_profile_bundle(
        bundle,
        workflow_name=args.workflow,
        preset_name=args.preset,
        only_valid=args.only_valid,
        only_invalid=args.only_invalid,
    )


def _build_profile_bundle_directory_payload(args: argparse.Namespace) -> dict[str, object]:
    inventory = build_workflow_profile_bundle_inventory(
        args.bundles_dir,
        workflow_name=args.workflow,
        preset_name=args.preset,
        only_valid=args.only_valid,
        only_invalid=args.only_invalid,
        bundle_name=args.bundle_name,
        only_clean_bundles=args.only_clean_bundles,
        only_problematic_bundles=args.only_problematic_bundles,
    )
    return {
        'bundles_dir': str(args.bundles_dir),
        'bundle_name_filter': args.bundle_name,
        'workflow_filter': args.workflow,
        'preset_filter': args.preset,
        'show_command': bool(getattr(args, 'show_command', False)),
        'summary_only': bool(getattr(args, 'summary_only', False)),
        'summary': inventory.build_summary(),
        'bundles': [item.to_dict() for item in inventory.records] if not getattr(args, 'summary_only', False) else [],
    }


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


def _profile_record_payload(item) -> dict[str, object]:
    if hasattr(item, "to_dict"):
        return item.to_dict()
    return {
        "name": getattr(item, "name", ""),
        "title": getattr(item, "title", ""),
        "workflow_name": getattr(item, "workflow_name", "unknown"),
        "preset_name": getattr(item, "preset_name", None),
        "profile_name": getattr(item, "profile_name", None),
        "profile_path": None if getattr(item, "profile_path", None) is None else str(getattr(item, "profile_path")),
        "valid": bool(getattr(item, "valid", False)),
        "missing_required_fields": list(getattr(item, "missing_required_fields", ())),
        "problems": list(getattr(item, "problems", ())),
        "command_preview": getattr(item, "command_preview", None),
    }


def _profile_bundle_comparison_entry_payload(item) -> dict[str, object]:
    return {
        "key": item.key,
        "status": item.status,
        "validity_changed": item.validity_changed,
        "command_changed": item.command_changed,
        "problems_changed": item.problems_changed,
        "payload_changed": getattr(item, "payload_changed", False),
        "left_item": None if item.left_item is None else _profile_record_payload(item.left_item),
        "right_item": None if item.right_item is None else _profile_record_payload(item.right_item),
    }


def _filter_profile_bundle_comparison_entries(entries, args: argparse.Namespace):
    filtered = list(entries)
    statuses = []
    if getattr(args, "only_added", False):
        statuses.append("added")
    if getattr(args, "only_removed", False):
        statuses.append("removed")
    if getattr(args, "only_changed", False):
        statuses.append("changed")
    if getattr(args, "only_unchanged", False):
        statuses.append("unchanged")
    if statuses:
        allowed = set(statuses)
        filtered = [item for item in filtered if item.status in allowed]
    return filtered


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


def _filter_history_entries(entries, command_name: str | None):
    if command_name is None:
        return list(entries)
    normalized = command_name.strip().lower()
    return [
        entry
        for entry in entries
        if entry.command_name.strip().lower() == normalized
    ]


def _print_history(path: Path, command_name: str | None, as_json: bool) -> int:
    entries = scan_history_directory(path)
    filtered_entries = _filter_history_entries(entries, command_name)
    summary = build_history_summary(filtered_entries)
    payload = {
        "command_filter": command_name,
        "summary": summary,
        "entries": [_history_payload(item) for item in filtered_entries],
    }
    if as_json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0

    print(f"Workflow history in {path}")
    if command_name:
        print(f"  Command filter: {command_name}")
    print(f"  Total entries: {summary['entry_count']}")
    print(f"  Successful: {summary['successful_count']}")
    print(f"  Failed: {summary['failed_count']}")
    print(f"  Reversible entries: {summary['reversible_entry_count']}")
    print(f"  Entries with reversible actions: {summary['entries_with_reversible_count']}")
    if summary["latest_created_at_utc"]:
        print(f"  Latest: {summary['latest_created_at_utc']}")
    if summary["apply_summary"]:
        apply_text = ", ".join(f"{key}={value}" for key, value in summary["apply_summary"].items())
        print(f"  Apply modes: {apply_text}")
    if summary["exit_code_summary"]:
        exit_text = ", ".join(f"{key}={value}" for key, value in summary["exit_code_summary"].items())
        print(f"  Exit codes: {exit_text}")
    if not filtered_entries:
        print("  No recognized run logs or execution journals found.")
        return 0

    if summary["command_summary"]:
        command_text = ", ".join(f"{key}={value}" for key, value in summary["command_summary"].items())
        print(f"  Commands: {command_text}")
    if summary["record_type_summary"]:
        record_text = ", ".join(f"{key}={value}" for key, value in summary["record_type_summary"].items())
        print(f"  Record types: {record_text}")

    for item in filtered_entries:
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


def _build_profile_directory_payload(args: argparse.Namespace) -> dict[str, object]:
    inventory = build_workflow_profile_inventory(
        args.profiles_dir,
        workflow_name=args.workflow,
        preset_name=args.preset,
        only_valid=args.only_valid,
        only_invalid=args.only_invalid,
    )
    profiles = [] if getattr(args, "summary_only", False) else [_profile_record_payload(item) for item in inventory.records]
    return {
        "profiles_dir": str(args.profiles_dir),
        "workflow_filter": args.workflow,
        "preset_filter": args.preset,
        "show_command": bool(getattr(args, "show_command", False)),
        "summary_only": bool(getattr(args, "summary_only", False)),
        "summary": inventory.build_summary(),
        "profiles": profiles,
    }


def _print_profile_list(args: argparse.Namespace) -> int:
    payload = _build_profile_directory_payload(args)
    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0

    summary = payload["summary"]
    print(f"Workflow profiles in {args.profiles_dir}")
    if args.workflow:
        print(f"  Workflow filter: {args.workflow}")
    if args.preset:
        print(f"  Preset filter: {args.preset}")
    print(f"  Total profiles: {summary['profile_count']}")
    print(f"  Valid: {summary['valid_count']}")
    print(f"  Invalid: {summary['invalid_count']}")

    if summary["workflow_summary"]:
        workflow_text = ", ".join(f"{key}={value}" for key, value in summary["workflow_summary"].items())
        print(f"  Workflows: {workflow_text}")
    if summary["preset_summary"]:
        preset_text = ", ".join(f"{key}={value}" for key, value in summary["preset_summary"].items())
        print(f"  Presets: {preset_text}")
    if summary["problem_summary"]:
        problem_text = ", ".join(f"{key}={value}" for key, value in summary["problem_summary"].items())
        print(f"  Problems: {problem_text}")

    if args.summary_only:
        return 0

    if not payload["profiles"]:
        print("  No matching workflow profiles found.")
        return 0

    for item in payload["profiles"]:
        status = "valid" if item["valid"] else "invalid"
        title = item["profile_name"] or item["title"] or item["name"]
        print(f"  - [{status}] {title} | workflow={item['workflow_name']} | preset={item['preset_name']}")
        if item["profile_path"]:
            print(f"    {item['profile_path']}")
        if args.show_command and item["command_preview"]:
            print(f"    Command: {item['command_preview']}")
        if item["problems"]:
            print("    Problems:")
            for problem in item["problems"]:
                print(f"      - {problem}")
    return 0


def _print_profile_audit(args: argparse.Namespace) -> int:
    payload = _build_profile_directory_payload(args)
    summary = payload["summary"]

    exit_code = 1 if summary["invalid_count"] > 0 else 0
    if getattr(args, "fail_on_empty", False) and summary["profile_count"] == 0:
        exit_code = 1

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return exit_code

    print(f"Workflow profile audit in {args.profiles_dir}")
    if args.workflow:
        print(f"  Workflow filter: {args.workflow}")
    if args.preset:
        print(f"  Preset filter: {args.preset}")
    print(f"  Total profiles: {summary['profile_count']}")
    print(f"  Valid: {summary['valid_count']}")
    print(f"  Invalid: {summary['invalid_count']}")
    if summary["problem_summary"]:
        problem_text = ", ".join(f"{key}={value}" for key, value in summary["problem_summary"].items())
        print(f"  Problems: {problem_text}")

    if args.summary_only:
        if summary["profile_count"] == 0:
            print("  No matching workflow profiles found.")
        elif exit_code == 0:
            print("  All matching profiles are valid.")
        return exit_code

    invalid_profiles = [item for item in payload["profiles"] if not item["valid"]]
    if not payload["profiles"]:
        print("  No matching workflow profiles found.")
        return exit_code

    if not invalid_profiles:
        print("  All matching profiles are valid.")
        return 0

    print("  Invalid profiles:")
    for item in invalid_profiles:
        title = item["profile_name"] or item["title"] or item["name"]
        print(f"    - {title} | workflow={item['workflow_name']} | preset={item['preset_name']}")
        if item["profile_path"]:
            print(f"      {item['profile_path']}")
        if args.show_command and item["command_preview"]:
            print(f"      Command: {item['command_preview']}")
        for problem in item["problems"]:
            print(f"      - {problem}")
    return exit_code


def _build_bundle_item_profile(item) -> WorkflowProfile | None:
    payload = getattr(item, "profile_payload", None)
    if not isinstance(payload, dict):
        return None
    raw_values = payload.get("values", {})
    if not isinstance(raw_values, dict):
        raw_values = {}
    profile_name = str(payload.get("profile_name", "")).strip() or (getattr(item, "profile_name", None) or getattr(item, "title", "") or getattr(item, "name", ""))
    preset_name = str(payload.get("preset", "")).strip() or str(getattr(item, "preset_name", "") or "")
    return WorkflowProfile(
        profile_name=profile_name or getattr(item, "name", "workflow-profile"),
        preset_name=preset_name,
        values=dict(raw_values),
    )


def _build_profile_bundle_run_payload(args: argparse.Namespace) -> tuple[int, dict[str, object]]:
    bundle = filter_workflow_profile_bundle(
        load_workflow_profile_bundle(args.path),
        workflow_name=args.workflow,
        preset_name=args.preset,
        only_valid=args.only_valid,
        only_invalid=args.only_invalid,
    )
    records = list(bundle.profiles)
    selected_summary = bundle.summary.to_dict()
    payload: dict[str, object] = {
        "bundle_path": str(args.path),
        "workflow_filter": args.workflow,
        "preset_filter": args.preset,
        "continue_on_error": bool(args.continue_on_error),
        "show_command": bool(args.show_command),
        "fail_on_empty": bool(args.fail_on_empty),
        "summary": {
            "selected_count": selected_summary["profile_count"],
            "valid_count": selected_summary["valid_count"],
            "invalid_count": selected_summary["invalid_count"],
            "workflow_summary": selected_summary["workflow_summary"],
            "preset_summary": selected_summary["preset_summary"],
            "problem_summary": selected_summary["problem_summary"],
            "executed_count": 0,
            "succeeded_count": 0,
            "failed_count": 0,
            "blocked_count": 0,
            "stopped_after_error": False,
            "exit_code_summary": {},
        },
        "runs": [],
    }

    if not records:
        exit_code = 1 if args.fail_on_empty else 0
        return exit_code, payload

    invalid_records = [item for item in records if not getattr(item, "valid", False)]
    if invalid_records:
        payload["runs"] = [
            {
                **_profile_record_payload(item),
                "delegated": False,
                "exit_code": None,
                "status": "invalid",
            }
            for item in invalid_records
        ]
        payload["summary"]["blocked_count"] = len(invalid_records)
        return 1, payload

    run_results: list[dict[str, object]] = []
    exit_code_summary: dict[str, int] = {}
    executed_count = 0
    succeeded_count = 0
    failed_count = 0
    blocked_count = 0
    stopped_after_error = False

    for item in records:
        profile = _build_bundle_item_profile(item)
        run_payload = {
            **_profile_record_payload(item),
            "delegated": False,
            "exit_code": None,
            "status": "pending",
        }

        if profile is None:
            run_payload["status"] = "invalid"
            run_payload["problems"] = list(run_payload.get("problems", [])) + ["Bundle item does not contain a usable profile payload."]
            run_results.append(run_payload)
            blocked_count += 1
            stopped_after_error = True
            break

        validation = validate_workflow_profile(profile)
        run_payload["command_preview"] = validation.command_preview
        run_payload["problems"] = list(validation.problems)

        if not validation.valid or not validation.command_argv or validation.workflow_name is None:
            run_payload["status"] = "invalid"
            run_results.append(run_payload)
            blocked_count += 1
            stopped_after_error = True
            break

        if args.json:
            captured_delegate_output = io.StringIO()
            with redirect_stdout(captured_delegate_output):
                delegated_exit_code = int(_run_delegated_workflow(validation.workflow_name, list(validation.command_argv[4:])))
        else:
            delegated_exit_code = int(_run_delegated_workflow(validation.workflow_name, list(validation.command_argv[4:])))
        run_payload["delegated"] = True
        run_payload["exit_code"] = delegated_exit_code
        run_payload["status"] = "ok" if delegated_exit_code == 0 else "error"
        run_results.append(run_payload)

        executed_count += 1
        exit_code_key = str(delegated_exit_code)
        exit_code_summary[exit_code_key] = exit_code_summary.get(exit_code_key, 0) + 1
        if delegated_exit_code == 0:
            succeeded_count += 1
        else:
            failed_count += 1
            if not args.continue_on_error:
                stopped_after_error = True
                break

    payload["runs"] = run_results
    payload["summary"]["executed_count"] = executed_count
    payload["summary"]["succeeded_count"] = succeeded_count
    payload["summary"]["failed_count"] = failed_count
    payload["summary"]["blocked_count"] = blocked_count
    payload["summary"]["stopped_after_error"] = stopped_after_error
    payload["summary"]["exit_code_summary"] = dict(sorted(exit_code_summary.items()))

    return (1 if failed_count > 0 or blocked_count > 0 else 0), payload


def _print_profile_bundle_run(args: argparse.Namespace) -> int:
    exit_code, payload = _build_profile_bundle_run_payload(args)
    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return exit_code

    summary = payload["summary"]
    print(f"Workflow profile bundle run from {args.path}")
    if args.workflow:
        print(f"  Workflow filter: {args.workflow}")
    if args.preset:
        print(f"  Preset filter: {args.preset}")
    print(f"  Selected profiles: {summary['selected_count']}")
    print(f"  Valid: {summary['valid_count']}")
    print(f"  Invalid: {summary['invalid_count']}")
    print(f"  Executed: {summary['executed_count']}")
    print(f"  Succeeded: {summary['succeeded_count']}")
    print(f"  Failed: {summary['failed_count']}")
    print(f"  Blocked: {summary['blocked_count']}")

    if summary["workflow_summary"]:
        workflow_text = ", ".join(f"{key}={value}" for key, value in summary["workflow_summary"].items())
        print(f"  Workflows: {workflow_text}")
    if summary["preset_summary"]:
        preset_text = ", ".join(f"{key}={value}" for key, value in summary["preset_summary"].items())
        print(f"  Presets: {preset_text}")
    if summary["problem_summary"]:
        problem_text = ", ".join(f"{key}={value}" for key, value in summary["problem_summary"].items())
        print(f"  Problems: {problem_text}")

    if not payload["runs"]:
        print("  No matching bundle profiles found.")
        return exit_code

    for item in payload["runs"]:
        title = item.get("profile_name") or item.get("title") or item.get("name")
        print(f"  - [{item['status']}] {title} | workflow={item['workflow_name']} | preset={item['preset_name']}")
        if item.get("profile_path"):
            print(f"    {item['profile_path']}")
        if args.show_command and item.get("command_preview"):
            print(f"    Command: {item['command_preview']}")
        if item.get("problems"):
            print("    Problems:")
            for problem in item["problems"]:
                print(f"      - {problem}")
    return exit_code


def _build_profile_run_payload(args: argparse.Namespace) -> tuple[int, dict[str, object]]:
    inventory = build_workflow_profile_inventory(
        args.profiles_dir,
        workflow_name=args.workflow,
        preset_name=args.preset,
        only_valid=args.only_valid,
        only_invalid=args.only_invalid,
    )
    records = list(inventory.records)
    selected_summary = inventory.build_summary()
    payload: dict[str, object] = {
        "profiles_dir": str(args.profiles_dir),
        "workflow_filter": args.workflow,
        "preset_filter": args.preset,
        "continue_on_error": bool(args.continue_on_error),
        "show_command": bool(args.show_command),
        "fail_on_empty": bool(args.fail_on_empty),
        "summary": {
            "selected_count": selected_summary["profile_count"],
            "valid_count": selected_summary["valid_count"],
            "invalid_count": selected_summary["invalid_count"],
            "workflow_summary": selected_summary["workflow_summary"],
            "preset_summary": selected_summary["preset_summary"],
            "problem_summary": selected_summary["problem_summary"],
            "executed_count": 0,
            "succeeded_count": 0,
            "failed_count": 0,
            "stopped_after_error": False,
            "exit_code_summary": {},
        },
        "runs": [],
    }

    if not records:
        exit_code = 1 if args.fail_on_empty else 0
        return exit_code, payload

    invalid_records = [item for item in records if not item.valid]
    if invalid_records:
        payload["runs"] = [
            {
                **_profile_record_payload(item),
                "delegated": False,
                "exit_code": None,
                "status": "invalid",
            }
            for item in invalid_records
        ]
        return 1, payload

    run_results: list[dict[str, object]] = []
    exit_code_summary: dict[str, int] = {}
    executed_count = 0
    succeeded_count = 0
    failed_count = 0
    stopped_after_error = False

    for item in records:
        profile = load_workflow_profile(item.profile_path)
        validation = validate_workflow_profile(profile)
        run_payload = {
            **_profile_record_payload(item),
            "delegated": False,
            "exit_code": None,
            "status": "pending",
            "command_preview": validation.command_preview,
            "problems": list(validation.problems),
        }

        if not validation.valid or not validation.command_argv or validation.workflow_name is None:
            run_payload["status"] = "invalid"
            run_results.append(run_payload)
            failed_count += 1
            stopped_after_error = True
            break

        if args.json:
            captured_delegate_output = io.StringIO()
            with redirect_stdout(captured_delegate_output):
                delegated_exit_code = int(_run_delegated_workflow(validation.workflow_name, list(validation.command_argv[4:])))
        else:
            delegated_exit_code = int(_run_delegated_workflow(validation.workflow_name, list(validation.command_argv[4:])))
        run_payload["delegated"] = True
        run_payload["exit_code"] = delegated_exit_code
        run_payload["status"] = "ok" if delegated_exit_code == 0 else "error"
        run_results.append(run_payload)

        executed_count += 1
        exit_code_key = str(delegated_exit_code)
        exit_code_summary[exit_code_key] = exit_code_summary.get(exit_code_key, 0) + 1
        if delegated_exit_code == 0:
            succeeded_count += 1
        else:
            failed_count += 1
            if not args.continue_on_error:
                stopped_after_error = True
                break

    payload["runs"] = run_results
    payload["summary"]["executed_count"] = executed_count
    payload["summary"]["succeeded_count"] = succeeded_count
    payload["summary"]["failed_count"] = failed_count
    payload["summary"]["stopped_after_error"] = stopped_after_error
    payload["summary"]["exit_code_summary"] = dict(sorted(exit_code_summary.items()))

    return (1 if failed_count > 0 else 0), payload


def _print_profile_run_dir(args: argparse.Namespace) -> int:
    exit_code, payload = _build_profile_run_payload(args)
    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return exit_code

    summary = payload["summary"]
    print(f"Workflow profile run in {args.profiles_dir}")
    if args.workflow:
        print(f"  Workflow filter: {args.workflow}")
    if args.preset:
        print(f"  Preset filter: {args.preset}")
    print(f"  Selected profiles: {summary['selected_count']}")
    print(f"  Valid: {summary['valid_count']}")
    print(f"  Invalid: {summary['invalid_count']}")
    print(f"  Executed: {summary['executed_count']}")
    print(f"  Succeeded: {summary['succeeded_count']}")
    print(f"  Failed: {summary['failed_count']}")

    if summary["workflow_summary"]:
        workflow_text = ", ".join(f"{key}={value}" for key, value in summary["workflow_summary"].items())
        print(f"  Workflows: {workflow_text}")
    if summary["preset_summary"]:
        preset_text = ", ".join(f"{key}={value}" for key, value in summary["preset_summary"].items())
        print(f"  Presets: {preset_text}")
    if summary["problem_summary"]:
        problem_text = ", ".join(f"{key}={value}" for key, value in summary["problem_summary"].items())
        print(f"  Problems: {problem_text}")

    runs = list(payload["runs"])
    if summary["selected_count"] == 0:
        print("  No matching workflow profiles found.")
        return exit_code

    if summary["invalid_count"] > 0:
        print("  Invalid matching profiles block execution.")
        for item in runs:
            title = item["profile_name"] or item["title"] or item["name"]
            print(f"    - {title} | workflow={item['workflow_name']} | preset={item['preset_name']}")
            if item["profile_path"]:
                print(f"      {item['profile_path']}")
            for problem in item["problems"]:
                print(f"      - {problem}")
        return exit_code

    if not runs:
        print("  No delegated workflow executions were recorded.")
        return exit_code

    print("  Run results:")
    for item in runs:
        title = item["profile_name"] or item["title"] or item["name"]
        exit_text = "n/a" if item["exit_code"] is None else str(item["exit_code"])
        print(f"    - [{item['status']}] {title} | workflow={item['workflow_name']} | preset={item['preset_name']} | exit={exit_text}")
        if item["profile_path"]:
            print(f"      {item['profile_path']}")
        if args.show_command and item["command_preview"]:
            print(f"      Command: {item['command_preview']}")

    if summary["stopped_after_error"]:
        print("  Execution stopped after the first delegated error.")
    elif args.continue_on_error and summary["failed_count"] > 0:
        print("  Execution continued after delegated errors.")

    return exit_code


def _build_profile_bundle_payload(bundle, args: argparse.Namespace) -> dict[str, object]:
    filtered_bundle = filter_workflow_profile_bundle(
        bundle,
        workflow_name=args.workflow,
        preset_name=args.preset,
        only_valid=args.only_valid,
        only_invalid=args.only_invalid,
    )
    profiles = [] if getattr(args, "summary_only", False) else [_profile_record_payload(item) for item in filtered_bundle.profiles]
    return {
        "bundle_path": None if getattr(args, "path", None) is None else str(args.path),
        "profiles_dir": filtered_bundle.profiles_dir,
        "workflow_filter": args.workflow,
        "preset_filter": args.preset,
        "show_command": bool(getattr(args, "show_command", False)),
        "summary_only": bool(getattr(args, "summary_only", False)),
        "summary": filtered_bundle.summary.to_dict(),
        "profiles": profiles,
    }


def _build_profile_bundle_merge_payload(args: argparse.Namespace) -> dict[str, object]:
    bundles = []
    for path in args.bundle_paths:
        loaded = load_workflow_profile_bundle(path)
        bundles.append(
            filter_workflow_profile_bundle(
                loaded,
                workflow_name=args.workflow,
                preset_name=args.preset,
                only_valid=args.only_valid,
                only_invalid=args.only_invalid,
            )
        )
    merged = merge_workflow_profile_bundles(bundles, prefer=args.prefer, profiles_dir="merged")
    profiles = [] if getattr(args, "summary_only", False) else [_profile_record_payload(item) for item in merged.profiles]
    return {
        "output_path": str(args.output_path),
        "bundle_paths": [str(item) for item in args.bundle_paths],
        "prefer": args.prefer,
        "workflow_filter": args.workflow,
        "preset_filter": args.preset,
        "summary": merged.summary.to_dict(),
        "profiles": profiles,
    }


def _build_profile_bundle_compare_payload(args: argparse.Namespace) -> dict[str, object]:
    left_bundle = filter_workflow_profile_bundle(
        load_workflow_profile_bundle(args.left_path),
        workflow_name=args.workflow,
        preset_name=args.preset,
        only_valid=args.only_valid,
        only_invalid=args.only_invalid,
    )
    right_bundle = filter_workflow_profile_bundle(
        load_workflow_profile_bundle(args.right_path),
        workflow_name=args.workflow,
        preset_name=args.preset,
        only_valid=args.only_valid,
        only_invalid=args.only_invalid,
    )
    comparison = compare_workflow_profile_bundles(left_bundle, right_bundle)
    entries = _filter_profile_bundle_comparison_entries(comparison.entries, args)

    added_count = sum(1 for item in entries if item.status == "added")
    removed_count = sum(1 for item in entries if item.status == "removed")
    changed_count = sum(1 for item in entries if item.status == "changed")
    unchanged_count = sum(1 for item in entries if item.status == "unchanged")
    changed_validity_count = sum(1 for item in entries if item.status == "changed" and item.validity_changed)
    changed_command_count = sum(1 for item in entries if item.status == "changed" and item.command_changed)
    changed_problem_count = sum(1 for item in entries if item.status == "changed" and item.problems_changed)
    changed_payload_count = sum(1 for item in entries if item.status == "changed" and getattr(item, "payload_changed", False))

    summary = {
        "left_profile_count": comparison.summary.left_profile_count,
        "right_profile_count": comparison.summary.right_profile_count,
        "added_count": added_count,
        "removed_count": removed_count,
        "changed_count": changed_count,
        "unchanged_count": unchanged_count,
        "changed_validity_count": changed_validity_count,
        "changed_command_count": changed_command_count,
        "changed_problem_count": changed_problem_count,
        "changed_payload_count": changed_payload_count,
        "entry_count": len(entries),
    }
    payload_entries = [] if getattr(args, "summary_only", False) else [_profile_bundle_comparison_entry_payload(item) for item in entries]
    return {
        "left_path": str(args.left_path),
        "right_path": str(args.right_path),
        "workflow_filter": args.workflow,
        "preset_filter": args.preset,
        "summary_only": bool(getattr(args, "summary_only", False)),
        "summary": summary,
        "entries": payload_entries,
    }


def _print_profile_bundle_extract(args: argparse.Namespace) -> int:
    try:
        bundle = load_workflow_profile_bundle(args.path)
        result = extract_workflow_profile_bundle(
            bundle,
            args.target_dir,
            workflow_name=args.workflow,
            preset_name=args.preset,
            only_valid=args.only_valid,
            only_invalid=args.only_invalid,
            overwrite=args.overwrite,
            preserve_structure=not args.flatten,
            bundle_path=str(args.path),
        )
    except Exception as exc:
        print(str(exc))
        return 1

    payload = result.to_dict()
    payload["workflow_filter"] = args.workflow
    payload["preset_filter"] = args.preset
    payload["flatten"] = bool(args.flatten)
    payload["bundle_path"] = str(args.path)

    exit_code = 0
    if getattr(args, "fail_on_empty", False) and result.selected_count == 0:
        exit_code = 1
    elif result.conflict_count > 0 or result.error_count > 0:
        exit_code = 1

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return exit_code

    print(f"Workflow profile bundle extract: {args.path}")
    print(f"  Target dir: {args.target_dir}")
    if args.workflow:
        print(f"  Workflow filter: {args.workflow}")
    if args.preset:
        print(f"  Preset filter: {args.preset}")
    print(f"  Selected profiles: {result.selected_count}")
    print(f"  Written: {result.written_count}")
    print(f"  Skipped: {result.skipped_count}")
    print(f"  Conflicts: {result.conflict_count}")
    print(f"  Errors: {result.error_count}")

    if not result.entries:
        print("  No matching bundle profiles found.")
        return exit_code

    for item in payload["entries"]:
        title = item["profile_name"] or item["relative_profile_path"] or item["target_path"]
        print(f"  - [{item['status']}] {title}")
        print(f"    {item['target_path']}")
        print(f"    Reason: {item['reason']}")
    return exit_code


def _print_profile_bundle_sync(args: argparse.Namespace) -> int:
    try:
        bundle = load_workflow_profile_bundle(args.path)
        result = sync_workflow_profile_bundle(
            bundle,
            args.target_dir,
            workflow_name=args.workflow,
            preset_name=args.preset,
            only_valid=args.only_valid,
            only_invalid=args.only_invalid,
            overwrite=args.overwrite,
            prune=args.prune,
            preserve_structure=not args.flatten,
            apply=args.apply,
            bundle_path=str(args.path),
        )
    except Exception as exc:
        print(str(exc))
        return 1

    payload = result.to_dict()
    payload["workflow_filter"] = args.workflow
    payload["preset_filter"] = args.preset
    payload["flatten"] = bool(args.flatten)
    payload["bundle_path"] = str(args.path)
    payload["summary_only"] = bool(getattr(args, "summary_only", False))

    exit_code = 0
    if getattr(args, "fail_on_empty", False) and result.selected_count == 0:
        exit_code = 1
    elif result.conflict_count > 0 or result.error_count > 0:
        exit_code = 1

    if args.json:
        if getattr(args, "summary_only", False):
            payload = {k: v for k, v in payload.items() if k != "entries"}
            payload["entries"] = []
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return exit_code

    mode_text = "apply" if args.apply else "preview"
    print(f"Workflow profile bundle sync ({mode_text}): {args.path}")
    print(f"  Target dir: {args.target_dir}")
    if args.workflow:
        print(f"  Workflow filter: {args.workflow}")
    if args.preset:
        print(f"  Preset filter: {args.preset}")
    print(f"  Selected profiles: {result.selected_count}")
    print(f"  Planned writes: {result.planned_write_count}")
    print(f"  Planned overwrites: {result.planned_overwrite_count}")
    print(f"  Planned deletes: {result.planned_delete_count}")
    print(f"  Written: {result.written_count}")
    print(f"  Overwritten: {result.overwritten_count}")
    print(f"  Deleted: {result.deleted_count}")
    print(f"  Skipped: {result.skipped_count}")
    print(f"  Conflicts: {result.conflict_count}")
    print(f"  Errors: {result.error_count}")

    if getattr(args, "summary_only", False):
        if result.selected_count == 0:
            print("  No matching bundle profiles found.")
        return exit_code

    if not result.entries:
        print("  No matching bundle profiles found.")
        return exit_code

    for item in payload["entries"]:
        title = item["profile_name"] or item["relative_profile_path"] or item["target_path"]
        print(f"  - [{item['status']}] {title}")
        print(f"    {item['target_path']}")
        print(f"    Reason: {item['reason']}")
        if args.show_command and item.get("command_preview"):
            print(f"    Command: {item['command_preview']}")
    return exit_code


def _print_profile_bundle_merge(args: argparse.Namespace) -> int:
    try:
        payload = _build_profile_bundle_merge_payload(args)
        bundles = []
        for path in args.bundle_paths:
            loaded = load_workflow_profile_bundle(path)
            bundles.append(
                filter_workflow_profile_bundle(
                    loaded,
                    workflow_name=args.workflow,
                    preset_name=args.preset,
                    only_valid=args.only_valid,
                    only_invalid=args.only_invalid,
                )
            )
        merged = merge_workflow_profile_bundles(bundles, prefer=args.prefer, profiles_dir="merged")
        output_path = Path(args.output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(merged.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception as exc:
        print(str(exc))
        return 1

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0

    summary = payload["summary"]
    print(f"Merged workflow profile bundles into: {args.output_path}")
    print(f"  Input bundles: {len(args.bundle_paths)}")
    print(f"  Prefer: {args.prefer}")
    print(f"  Total profiles: {summary['profile_count']}")
    print(f"  Valid: {summary['valid_count']}")
    print(f"  Invalid: {summary['invalid_count']}")
    if summary["workflow_summary"]:
        workflow_text = ", ".join(f"{key}={value}" for key, value in summary["workflow_summary"].items())
        print(f"  Workflows: {workflow_text}")
    if summary["preset_summary"]:
        preset_text = ", ".join(f"{key}={value}" for key, value in summary["preset_summary"].items())
        print(f"  Presets: {preset_text}")
    return 0


def _print_profile_bundle_compare(args: argparse.Namespace) -> int:
    try:
        payload = _build_profile_bundle_compare_payload(args)
    except Exception as exc:
        print(str(exc))
        return 1

    summary = payload["summary"]
    exit_code = 0
    if getattr(args, "fail_on_empty", False) and summary["entry_count"] == 0:
        exit_code = 1
    if getattr(args, "fail_on_changes", False) and (summary["added_count"] > 0 or summary["removed_count"] > 0 or summary["changed_count"] > 0):
        exit_code = 1

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return exit_code

    print(f"Workflow profile bundle compare: {args.left_path} vs {args.right_path}")
    if args.workflow:
        print(f"  Workflow filter: {args.workflow}")
    if args.preset:
        print(f"  Preset filter: {args.preset}")
    print(f"  Left profiles: {summary['left_profile_count']}")
    print(f"  Right profiles: {summary['right_profile_count']}")
    print(f"  Added: {summary['added_count']}")
    print(f"  Removed: {summary['removed_count']}")
    print(f"  Changed: {summary['changed_count']}")
    print(f"  Unchanged: {summary['unchanged_count']}")

    if args.summary_only:
        if summary["entry_count"] == 0:
            print("  No matching bundle comparison entries found.")
        return exit_code

    if not payload["entries"]:
        print("  No matching bundle comparison entries found.")
        return exit_code

    for item in payload["entries"]:
        left_item = item["left_item"]
        right_item = item["right_item"]
        print(f"  - [{item['status']}] {item['key']}")
        if left_item is not None:
            print(f"    Left: {left_item['workflow_name']} | preset={left_item['preset_name']} | valid={left_item['valid']}")
            if args.show_command and left_item["command_preview"]:
                print(f"      Command: {left_item['command_preview']}")
        if right_item is not None:
            print(f"    Right: {right_item['workflow_name']} | preset={right_item['preset_name']} | valid={right_item['valid']}")
            if args.show_command and right_item["command_preview"]:
                print(f"      Command: {right_item['command_preview']}")
        detail_flags = []
        if item["validity_changed"]:
            detail_flags.append("validity")
        if item["command_changed"]:
            detail_flags.append("command")
        if item["problems_changed"]:
            detail_flags.append("problems")
        if item.get("payload_changed"):
            detail_flags.append("payload")
        if detail_flags:
            print(f"    Changed fields: {', '.join(detail_flags)}")
    return exit_code


def _print_profile_bundle_write(args: argparse.Namespace) -> int:
    try:
        output_path = write_workflow_profile_bundle(
            args.output_path,
            args.profiles_dir,
            workflow_name=args.workflow,
            preset_name=args.preset,
            only_valid=args.only_valid,
            only_invalid=args.only_invalid,
        )
        bundle = load_workflow_profile_bundle(output_path)
    except Exception as exc:
        print(str(exc))
        return 1

    payload = _build_profile_bundle_payload(bundle, args)
    payload["output_path"] = str(output_path)
    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0

    summary = payload["summary"]
    print(f"Wrote workflow profile bundle: {output_path}")
    print(f"  Profiles dir: {payload['profiles_dir']}")
    print(f"  Total profiles: {summary['profile_count']}")
    print(f"  Valid: {summary['valid_count']}")
    print(f"  Invalid: {summary['invalid_count']}")
    if summary["duplicate_profile_name_summary"]:
        dup_text = ", ".join(f"{key}={value}" for key, value in summary["duplicate_profile_name_summary"].items())
        print(f"  Duplicate profile names: {dup_text}")
    if summary["duplicate_command_summary"]:
        print(f"  Duplicate commands: {summary['duplicate_command_count']}")
    return 0


def _print_profile_bundle_show(args: argparse.Namespace) -> int:
    try:
        bundle = load_workflow_profile_bundle(args.path)
    except Exception as exc:
        print(str(exc))
        return 1

    payload = _build_profile_bundle_payload(bundle, args)
    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0

    summary = payload["summary"]
    print(f"Workflow profile bundle: {args.path}")
    print(f"  Profiles dir: {payload['profiles_dir']}")
    if args.workflow:
        print(f"  Workflow filter: {args.workflow}")
    if args.preset:
        print(f"  Preset filter: {args.preset}")
    print(f"  Total profiles: {summary['profile_count']}")
    print(f"  Valid: {summary['valid_count']}")
    print(f"  Invalid: {summary['invalid_count']}")
    if summary["workflow_summary"]:
        workflow_text = ", ".join(f"{key}={value}" for key, value in summary["workflow_summary"].items())
        print(f"  Workflows: {workflow_text}")
    if summary["preset_summary"]:
        preset_text = ", ".join(f"{key}={value}" for key, value in summary["preset_summary"].items())
        print(f"  Presets: {preset_text}")
    if summary["problem_summary"]:
        problem_text = ", ".join(f"{key}={value}" for key, value in summary["problem_summary"].items())
        print(f"  Problems: {problem_text}")
    if summary["duplicate_profile_name_summary"]:
        dup_text = ", ".join(f"{key}={value}" for key, value in summary["duplicate_profile_name_summary"].items())
        print(f"  Duplicate profile names: {dup_text}")
    if summary["duplicate_command_summary"]:
        print(f"  Duplicate commands: {summary['duplicate_command_count']}")

    if args.summary_only:
        return 0

    if not payload["profiles"]:
        print("  No matching workflow bundle profiles found.")
        return 0

    for item in payload["profiles"]:
        status = "valid" if item["valid"] else "invalid"
        title = item["profile_name"] or item["title"] or item["name"]
        print(f"  - [{status}] {title} | workflow={item['workflow_name']} | preset={item['preset_name']}")
        if item["relative_profile_path"]:
            print(f"    {item['relative_profile_path']}")
        if args.show_command and item["command_preview"]:
            print(f"    Command: {item['command_preview']}")
        if item["problems"]:
            print("    Problems:")
            for problem in item["problems"]:
                print(f"      - {problem}")
    return 0


def _print_profile_bundle_audit(args: argparse.Namespace) -> int:
    try:
        bundle = load_workflow_profile_bundle(args.path)
    except Exception as exc:
        print(str(exc))
        return 1

    payload = _build_profile_bundle_payload(bundle, args)
    summary = payload["summary"]
    exit_code = 1 if summary["invalid_count"] > 0 else 0
    if getattr(args, "fail_on_empty", False) and summary["profile_count"] == 0:
        exit_code = 1

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return exit_code

    print(f"Workflow profile bundle audit: {args.path}")
    if args.workflow:
        print(f"  Workflow filter: {args.workflow}")
    if args.preset:
        print(f"  Preset filter: {args.preset}")
    print(f"  Total profiles: {summary['profile_count']}")
    print(f"  Valid: {summary['valid_count']}")
    print(f"  Invalid: {summary['invalid_count']}")
    if summary["problem_summary"]:
        problem_text = ", ".join(f"{key}={value}" for key, value in summary["problem_summary"].items())
        print(f"  Problems: {problem_text}")

    if args.summary_only:
        if summary["profile_count"] == 0:
            print("  No matching workflow bundle profiles found.")
        elif exit_code == 0:
            print("  All matching bundle profiles are valid.")
        return exit_code

    invalid_profiles = [item for item in payload["profiles"] if not item["valid"]]
    if not payload["profiles"]:
        print("  No matching workflow bundle profiles found.")
        return exit_code
    if not invalid_profiles:
        print("  All matching bundle profiles are valid.")
        return 0

    print("  Invalid bundle profiles:")
    for item in invalid_profiles:
        title = item["profile_name"] or item["title"] or item["name"]
        print(f"    - {title} | workflow={item['workflow_name']} | preset={item['preset_name']}")
        if item["relative_profile_path"]:
            print(f"      {item['relative_profile_path']}")
        if args.show_command and item["command_preview"]:
            print(f"      Command: {item['command_preview']}")
        for problem in item["problems"]:
            print(f"      - {problem}")
    return exit_code


def _print_profile_bundle_list_dir(args: argparse.Namespace) -> int:
    try:
        payload = _build_profile_bundle_directory_payload(args)
    except Exception as exc:
        print(str(exc))
        return 1

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0

    summary = payload['summary']
    print(f"Workflow profile bundles in {args.bundles_dir}")
    if args.bundle_name:
        print(f"  Bundle name filter: {args.bundle_name}")
    if args.workflow:
        print(f"  Workflow filter: {args.workflow}")
    if args.preset:
        print(f"  Preset filter: {args.preset}")
    print(f"  Total bundles: {summary['bundle_count']}")
    print(f"  Clean bundles: {summary['clean_bundle_count']}")
    print(f"  Problematic bundles: {summary['problematic_bundle_count']}")
    print(f"  Total profiles: {summary['profile_count']}")
    print(f"  Valid profiles: {summary['valid_count']}")
    print(f"  Invalid profiles: {summary['invalid_count']}")
    if summary['problem_summary']:
        problem_text = ", ".join(f"{key}={value}" for key, value in summary['problem_summary'].items())
        print(f"  Problems: {problem_text}")
    if args.summary_only:
        return 0
    if not payload['bundles']:
        print("  No matching workflow profile bundles found.")
        return 0
    for item in payload['bundles']:
        status = 'clean' if item['clean_bundle'] else 'problematic'
        print(f"  - [{status}] {item['bundle_name']} | profiles={item['profile_count']} | valid={item['valid_count']} | invalid={item['invalid_count']}")
        print(f"    {item['bundle_path']}")
        if item['errors']:
            for error in item['errors']:
                print(f"    - {error}")
        elif args.show_command:
            try:
                bundle = _load_filtered_bundle_for_record(type('R', (), {'bundle_path': Path(item['bundle_path'])})(), args)
            except Exception as exc:
                print(f"    - {exc}")
            else:
                for profile in bundle.profiles:
                    if profile.command_preview:
                        title = profile.profile_name or profile.title or profile.name
                        print(f"    Command [{title}]: {profile.command_preview}")
    return 0


def _print_profile_bundle_audit_dir(args: argparse.Namespace) -> int:
    try:
        payload = _build_profile_bundle_directory_payload(args)
    except Exception as exc:
        print(str(exc))
        return 1

    summary = payload['summary']
    exit_code = 1 if summary['problematic_bundle_count'] > 0 else 0
    if getattr(args, 'fail_on_empty', False) and summary['bundle_count'] == 0:
        exit_code = 1

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return exit_code

    print(f"Workflow profile bundle audit in {args.bundles_dir}")
    print(f"  Total bundles: {summary['bundle_count']}")
    print(f"  Clean bundles: {summary['clean_bundle_count']}")
    print(f"  Problematic bundles: {summary['problematic_bundle_count']}")
    print(f"  Total profiles: {summary['profile_count']}")
    print(f"  Invalid profiles: {summary['invalid_count']}")
    if summary['problem_summary']:
        problem_text = ", ".join(f"{key}={value}" for key, value in summary['problem_summary'].items())
        print(f"  Problems: {problem_text}")
    if args.summary_only:
        if summary['bundle_count'] == 0:
            print('  No matching workflow profile bundles found.')
        elif exit_code == 0:
            print('  All matching workflow profile bundles are clean.')
        return exit_code
    if not payload['bundles']:
        print('  No matching workflow profile bundles found.')
        return exit_code
    problematic = [item for item in payload['bundles'] if not item['clean_bundle']]
    if not problematic:
        print('  All matching workflow profile bundles are clean.')
        return 0
    print('  Problematic bundles:')
    for item in problematic:
        print(f"    - {item['bundle_name']} | profiles={item['profile_count']} | invalid={item['invalid_count']}")
        print(f"      {item['bundle_path']}")
        for error in item['errors']:
            print(f"      - {error}")
    return exit_code


def _build_profile_bundle_run_dir_payload(args: argparse.Namespace) -> tuple[int, dict[str, object]]:
    inventory = build_workflow_profile_bundle_inventory(
        args.bundles_dir,
        workflow_name=args.workflow,
        preset_name=args.preset,
        only_valid=args.only_valid,
        only_invalid=args.only_invalid,
        bundle_name=args.bundle_name,
        only_clean_bundles=args.only_clean_bundles,
        only_problematic_bundles=args.only_problematic_bundles,
    )
    records = list(inventory.records)
    payload: dict[str, object] = {
        'bundles_dir': str(args.bundles_dir),
        'bundle_name_filter': args.bundle_name,
        'workflow_filter': args.workflow,
        'preset_filter': args.preset,
        'continue_on_error': bool(args.continue_on_error),
        'show_command': bool(args.show_command),
        'fail_on_empty': bool(args.fail_on_empty),
        'summary': {
            'selected_bundle_count': len(records),
            'clean_bundle_count': sum(1 for item in records if item.clean_bundle),
            'problematic_bundle_count': sum(1 for item in records if not item.clean_bundle),
            'selected_profile_count': sum(item.profile_count for item in records),
            'valid_count': sum(item.valid_count for item in records),
            'invalid_count': sum(item.invalid_count for item in records),
            'executed_count': 0,
            'succeeded_count': 0,
            'failed_count': 0,
            'blocked_count': 0,
            'stopped_after_error': False,
            'exit_code_summary': {},
        },
        'bundles': [],
    }
    if not records:
        return (1 if args.fail_on_empty else 0), payload

    overall_exit = 0
    exit_code_summary: dict[str, int] = {}
    for record in records:
        if not record.loadable:
            bundle_payload = {
                'bundle_name': record.bundle_name,
                'bundle_path': str(record.bundle_path),
                'status': 'unreadable',
                'summary': {
                    'selected_count': 0,
                    'executed_count': 0,
                    'succeeded_count': 0,
                    'failed_count': 0,
                    'blocked_count': 0,
                    'stopped_after_error': False,
                    'exit_code_summary': {},
                },
                'runs': [],
                'errors': list(record.errors),
            }
            payload['bundles'].append(bundle_payload)
            payload['summary']['blocked_count'] += 1
            overall_exit = 1
            if not args.continue_on_error:
                payload['summary']['stopped_after_error'] = True
                break
            continue

        ns = argparse.Namespace(
            path=record.bundle_path,
            workflow=args.workflow,
            preset=args.preset,
            only_valid=args.only_valid,
            only_invalid=args.only_invalid,
            show_command=args.show_command,
            continue_on_error=args.continue_on_error,
            fail_on_empty=False,
            json=bool(getattr(args, 'json', False)),
        )
        bundle_exit, bundle_payload = _build_profile_bundle_run_payload(ns)
        bundle_payload = {
            'bundle_name': record.bundle_name,
            'bundle_path': str(record.bundle_path),
            'status': 'ok' if bundle_exit == 0 else 'error',
            'summary': bundle_payload['summary'],
            'runs': bundle_payload['runs'],
            'errors': [],
        }
        payload['bundles'].append(bundle_payload)
        summary = bundle_payload['summary']
        payload['summary']['executed_count'] += summary['executed_count']
        payload['summary']['succeeded_count'] += summary['succeeded_count']
        payload['summary']['failed_count'] += summary['failed_count']
        payload['summary']['blocked_count'] += summary['blocked_count']
        for code, count in summary['exit_code_summary'].items():
            exit_code_summary[code] = exit_code_summary.get(code, 0) + count
        if bundle_exit != 0:
            overall_exit = 1
            if not args.continue_on_error:
                payload['summary']['stopped_after_error'] = True
                break
    payload['summary']['exit_code_summary'] = dict(sorted(exit_code_summary.items()))
    return overall_exit, payload


def _print_profile_bundle_run_dir(args: argparse.Namespace) -> int:
    try:
        exit_code, payload = _build_profile_bundle_run_dir_payload(args)
    except Exception as exc:
        print(str(exc))
        return 1
    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return exit_code
    summary = payload['summary']
    print(f"Workflow profile bundle run in {args.bundles_dir}")
    print(f"  Selected bundles: {summary['selected_bundle_count']}")
    print(f"  Selected profiles: {summary['selected_profile_count']}")
    print(f"  Executed: {summary['executed_count']}")
    print(f"  Succeeded: {summary['succeeded_count']}")
    print(f"  Failed: {summary['failed_count']}")
    print(f"  Blocked: {summary['blocked_count']}")
    if not payload['bundles']:
        print('  No matching workflow profile bundles found.')
        return exit_code
    for item in payload['bundles']:
        print(f"  - [{item['status']}] {item['bundle_name']}")
        print(f"    {item['bundle_path']}")
        if item['errors']:
            for error in item['errors']:
                print(f"    - {error}")
        elif item['summary']['executed_count']:
            print(f"    Executed={item['summary']['executed_count']} Succeeded={item['summary']['succeeded_count']} Failed={item['summary']['failed_count']}")
    return exit_code


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
            "  media-manager workflow profile-list --profiles-dir <PROFILES_DIR>\n"
            "  media-manager workflow profile-audit --profiles-dir <PROFILES_DIR>\n"
            "  media-manager workflow profile-bundle-write bundles/profiles.json --profiles-dir <PROFILES_DIR>\n"
            "  media-manager workflow profile-bundle-show bundles/profiles.json\n"
            "  media-manager workflow profile-bundle-audit bundles/profiles.json\n"
            "  media-manager workflow profile-bundle-merge bundles/merged.json bundles/one.json bundles/two.json\n"
            "  media-manager workflow profile-bundle-compare bundles/left.json bundles/right.json\n"
            "  media-manager workflow profile-bundle-run bundles/profiles.json\n"
            "  media-manager workflow profile-bundle-list-dir --bundles-dir <BUNDLES_DIR>\n"
            "  media-manager workflow profile-bundle-audit-dir --bundles-dir <BUNDLES_DIR>\n"
            "  media-manager workflow profile-bundle-run-dir --bundles-dir <BUNDLES_DIR>\n"
            "  media-manager workflow profile-run <PROFILE.json> --show-command\n"
            "  media-manager workflow profile-run-dir --profiles-dir <PROFILES_DIR> --only-valid\n"
            "  media-manager workflow history --path <RUNS_DIR>\n"
            "  media-manager workflow history --path <RUNS_DIR> --command organize\n"
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
        return _print_history(args.path, args.command, args.json)
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
    if args.workflow_command == "profile-list":
        return _print_profile_list(args)
    if args.workflow_command == "profile-audit":
        return _print_profile_audit(args)
    if args.workflow_command == "profile-bundle-write":
        return _print_profile_bundle_write(args)
    if args.workflow_command == "profile-bundle-show":
        return _print_profile_bundle_show(args)
    if args.workflow_command == "profile-bundle-audit":
        return _print_profile_bundle_audit(args)
    if args.workflow_command == "profile-bundle-extract":
        return _print_profile_bundle_extract(args)
    if args.workflow_command == "profile-bundle-sync":
        return _print_profile_bundle_sync(args)
    if args.workflow_command == "profile-bundle-merge":
        return _print_profile_bundle_merge(args)
    if args.workflow_command == "profile-bundle-compare":
        return _print_profile_bundle_compare(args)
    if args.workflow_command == "profile-bundle-run":
        return _print_profile_bundle_run(args)
    if args.workflow_command == "profile-bundle-list-dir":
        return _print_profile_bundle_list_dir(args)
    if args.workflow_command == "profile-bundle-audit-dir":
        return _print_profile_bundle_audit_dir(args)
    if args.workflow_command == "profile-bundle-run-dir":
        return _print_profile_bundle_run_dir(args)
    if args.workflow_command == "profile-run":
        return _run_workflow_profile(args.path, args.show_command)
    if args.workflow_command == "profile-run-dir":
        return _print_profile_run_dir(args)
    if args.workflow_command == "run":
        return _run_delegated_workflow(args.workflow, list(args.args))

    parser.print_help()
    return 2
