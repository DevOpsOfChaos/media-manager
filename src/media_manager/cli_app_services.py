from __future__ import annotations

import argparse
import json
from pathlib import Path

from .core.app_services import (
    build_app_home_state,
    read_json_object,
    write_json_object,
    write_report_service_bundle,
)
from .core.app_startup import build_app_startup_state
from .core.gui_app_service_view_models import (
    build_ui_app_service_view_models,
    summarize_ui_app_service_view_models,
    write_ui_app_service_view_models,
)
from .core.gui_desktop_runtime_state import (
    build_gui_desktop_runtime_state,
    summarize_gui_desktop_runtime_state,
    write_gui_desktop_runtime_state,
)
from .core.gui_command_plan import (
    build_open_people_bundle_plan,
    build_people_review_apply_command_plan,
    build_profile_command_plan,
    write_command_plan,
)
from .core.gui_page_contracts import build_gui_navigation_state, build_gui_page_catalog
from .core.gui_state_store import (
    add_recent_path,
    build_default_gui_state,
    build_gui_state_summary,
    load_gui_state,
    register_people_bundle,
    set_active_page,
    write_gui_state,
)
from .core.people_review_audit import build_people_review_apply_preview, write_people_review_apply_preview
from .core.people_review_bundle_validator import validate_people_review_bundle, write_people_review_bundle_validation


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="media-manager app-services",
        description="GUI-facing service helpers for Media Manager frontends.",
    )
    subparsers = parser.add_subparsers(dest="service_command")

    home = subparsers.add_parser("home-state", help="Build a GUI dashboard/home state from profiles, runs, and optional people bundle.")
    home.add_argument("--profile-dir", type=Path, help="Directory containing app profile JSON files.")
    home.add_argument("--run-dir", type=Path, help="Run artifact root directory.")
    home.add_argument("--people-bundle-dir", type=Path, help="Optional people review bundle directory.")
    home.add_argument("--active-page", default="dashboard", help="Active GUI page id. Default: dashboard.")
    home.add_argument("--run-limit", type=int, default=10, help="Maximum recent runs to include. Default: 10.")
    home.add_argument("--out", type=Path, help="Optional output JSON path.")
    home.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")

    startup = subparsers.add_parser("startup-state", help="Build the first state object a future GUI can load at startup.")
    startup.add_argument("--gui-state", type=Path, help="Optional persisted GUI state JSON path.")
    startup.add_argument("--profile-dir", type=Path, help="Directory containing app profile JSON files.")
    startup.add_argument("--run-dir", type=Path, help="Run artifact root directory.")
    startup.add_argument("--people-bundle-dir", type=Path, help="Optional people review bundle directory.")
    startup.add_argument("--active-page", help="Override active GUI page id.")
    startup.add_argument("--out", type=Path, help="Optional output JSON path.")
    startup.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")

    desktop = subparsers.add_parser("desktop-runtime", help="Build the headless desktop runtime state consumed by the future Qt UI.")
    desktop.add_argument("--profile-dir", type=Path, help="Directory containing app profile JSON files.")
    desktop.add_argument("--run-dir", type=Path, help="Run artifact root directory.")
    desktop.add_argument("--people-bundle-dir", type=Path, help="Optional people review bundle directory.")
    desktop.add_argument("--home-state-json", type=Path, help="Optional prebuilt app home-state JSON.")
    desktop.add_argument("--settings-json", type=Path, help="Optional GUI settings JSON.")
    desktop.add_argument("--view-state-json", type=Path, help="Optional GUI view-state JSON.")
    desktop.add_argument("--active-page", default="dashboard", help="Active GUI page id. Default: dashboard.")
    desktop.add_argument("--language", choices=["en", "de"], help="GUI language. Supported: en, de.")
    desktop.add_argument("--theme", help="GUI theme. Default comes from settings or modern-dark.")
    desktop.add_argument("--density", choices=["compact", "comfortable", "spacious"], help="GUI density.")
    desktop.add_argument("--out-dir", type=Path, help="Optional directory for split desktop-runtime JSON files.")
    desktop.add_argument("--out", type=Path, help="Optional output JSON path.")
    desktop.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")

    view_models = subparsers.add_parser("ui-view-models", help="Build product UI app-service view models for future Qt pages.")
    view_models.add_argument("--profile-dir", type=Path, help="Directory containing app profile JSON files.")
    view_models.add_argument("--run-dir", type=Path, help="Run artifact root directory.")
    view_models.add_argument("--people-bundle-dir", type=Path, help="Optional people review bundle directory.")
    view_models.add_argument("--home-state-json", type=Path, help="Optional prebuilt app home-state JSON.")
    view_models.add_argument("--active-page", default="dashboard", help="Active GUI page id. Default: dashboard.")
    view_models.add_argument("--language", choices=["en", "de"], help="GUI language. Supported: en, de.")
    view_models.add_argument("--out-dir", type=Path, help="Optional directory for split view-model JSON files.")
    view_models.add_argument("--out", type=Path, help="Optional output JSON path.")
    view_models.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")

    report = subparsers.add_parser("report-bundle", help="Build ui_state, plan_snapshot, and action_model for one report.")
    report.add_argument("--command", required=True, help="Command name for the report.")
    report.add_argument("--report-json", type=Path, required=True, help="Report JSON path.")
    report.add_argument("--command-json", type=Path, help="Optional command.json path.")
    report.add_argument("--run-id", help="Optional run id.")
    report.add_argument("--entry-limit", type=int, default=200, help="Maximum plan snapshot rows. Default: 200.")
    report.add_argument("--out-dir", type=Path, required=True, help="Directory to write derived service artifacts.")
    report.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")

    pages = subparsers.add_parser("pages", help="Print GUI page contracts and navigation state.")
    pages.add_argument("--active-page", default="dashboard", help="Active GUI page id. Default: dashboard.")
    pages.add_argument("--out", type=Path, help="Optional output JSON path.")
    pages.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")

    workspace = subparsers.add_parser("workspace", help="Create, show, or update persisted GUI workspace state.")
    workspace_sub = workspace.add_subparsers(dest="workspace_command")

    workspace_init = workspace_sub.add_parser("init", help="Create a GUI state JSON file.")
    workspace_init.add_argument("--state-json", type=Path, required=True, help="GUI state JSON path.")
    workspace_init.add_argument("--workspace-root", type=Path, help="Optional local workspace root.")
    workspace_init.add_argument("--overwrite", action="store_true", help="Overwrite an existing state file.")
    workspace_init.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")

    workspace_show = workspace_sub.add_parser("show", help="Show a GUI state JSON summary.")
    workspace_show.add_argument("--state-json", type=Path, required=True, help="GUI state JSON path.")
    workspace_show.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")

    workspace_page = workspace_sub.add_parser("set-page", help="Set the active GUI page.")
    workspace_page.add_argument("--state-json", type=Path, required=True, help="GUI state JSON path.")
    workspace_page.add_argument("--page-id", required=True, help="Active page id to store.")
    workspace_page.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")

    workspace_recent = workspace_sub.add_parser("add-recent", help="Add a path to a GUI recent-list section.")
    workspace_recent.add_argument("--state-json", type=Path, required=True, help="GUI state JSON path.")
    workspace_recent.add_argument("--section", choices=["run_dirs", "profile_dirs", "people_bundle_dirs", "catalog_paths"], required=True)
    workspace_recent.add_argument("--path", required=True, help="Path to add.")
    workspace_recent.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")

    workspace_people = workspace_sub.add_parser("register-people-bundle", help="Remember a people review bundle in GUI state.")
    workspace_people.add_argument("--state-json", type=Path, required=True, help="GUI state JSON path.")
    workspace_people.add_argument("--bundle-dir", type=Path, required=True, help="People review bundle directory.")
    workspace_people.add_argument("--catalog", type=Path, help="Optional people catalog path.")
    workspace_people.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")

    preview = subparsers.add_parser("people-review-preview", help="Preview people review apply without writing the catalog.")
    preview.add_argument("--catalog", type=Path, required=True, help="People catalog JSON path.")
    preview.add_argument("--workflow-json", type=Path, required=True, help="Edited people review workflow JSON.")
    preview.add_argument("--report-json", type=Path, required=True, help="Original people scan report JSON with encodings.")
    preview.add_argument("--out-catalog", type=Path, help="Optional output catalog path that review-apply would write.")
    preview.add_argument("--out", type=Path, help="Optional preview output JSON path.")
    preview.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")

    validate_bundle = subparsers.add_parser("validate-people-bundle", help="Validate a people review bundle directory for GUI use.")
    validate_bundle.add_argument("--bundle-dir", type=Path, required=True, help="People review bundle directory.")
    validate_bundle.add_argument("--out", type=Path, help="Optional validation output JSON path.")
    validate_bundle.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")

    command_plan = subparsers.add_parser("command-plan", help="Build non-executing GUI command plans.")
    command_plan_sub = command_plan.add_subparsers(dest="plan_command")

    plan_profile = command_plan_sub.add_parser("profile", help="Build a command plan from an app profile.")
    plan_profile.add_argument("profile", type=Path, help="App profile JSON path.")
    plan_profile.add_argument("--out", type=Path, help="Optional output JSON path.")
    plan_profile.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")

    plan_people_apply = command_plan_sub.add_parser("people-review-apply", help="Build a command plan for applying reviewed people.")
    plan_people_apply.add_argument("--catalog", type=Path, required=True)
    plan_people_apply.add_argument("--workflow-json", type=Path, required=True)
    plan_people_apply.add_argument("--report-json", type=Path, required=True)
    plan_people_apply.add_argument("--out-catalog", type=Path)
    plan_people_apply.add_argument("--dry-run", action="store_true")
    plan_people_apply.add_argument("--out", type=Path, help="Optional output JSON path.")
    plan_people_apply.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")

    plan_open_bundle = command_plan_sub.add_parser("open-people-bundle", help="Build a command plan for opening/validating a people review bundle.")
    plan_open_bundle.add_argument("--bundle-dir", type=Path, required=True)
    plan_open_bundle.add_argument("--out", type=Path, help="Optional output JSON path.")
    plan_open_bundle.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")
    return parser


def _print_home_text(payload: dict[str, object]) -> None:
    profiles = payload.get("profiles", {})
    runs = payload.get("runs", {})
    print("Media Manager GUI home state")
    if isinstance(profiles, dict):
        summary = profiles.get("summary", {})
        if isinstance(summary, dict):
            print(f"  Profiles: {summary.get('profile_count', 0)}")
    if isinstance(runs, dict):
        summary = runs.get("summary", {})
        if isinstance(summary, dict):
            print(f"  Recent runs: {summary.get('run_count', 0)}")
    print(f"  Suggested next step: {payload.get('suggested_next_step')}")


def _print_report_bundle_text(payload: dict[str, object]) -> None:
    print("Report service bundle")
    print(f"  Command: {payload.get('command')}")
    print(f"  Service dir: {payload.get('service_dir')}")
    for path in payload.get("written_files", []):
        print(f"  - {path}")


def _print_pages_text(payload: dict[str, object]) -> None:
    catalog = payload.get("catalog", {})
    print("GUI page contracts")
    if isinstance(catalog, dict):
        print(f"  Pages: {catalog.get('page_count', 0)}")
        for page in catalog.get("pages", []):
            if isinstance(page, dict):
                print(f"  - {page.get('page_id')}: {page.get('title')}")


def _print_preview_text(payload: dict[str, object]) -> None:
    summary = payload.get("summary", {})
    print("People review apply preview")
    print(f"  Status: {payload.get('status')}")
    print(f"  Safe to apply: {payload.get('safe_to_apply')}")
    if isinstance(summary, dict):
        print(f"  Ready groups: {summary.get('ready_group_count', 0)}")
        print(f"  Blocked groups: {summary.get('blocked_group_count', 0)}")
        print(f"  Embeddings to add: {summary.get('embeddings_added', 0)}")
    print(f"  Next action: {payload.get('next_action')}")


def _print_validation_text(payload: dict[str, object]) -> None:
    summary = payload.get("summary", {})
    print("People review bundle validation")
    print(f"  Status: {payload.get('status')}")
    print(f"  Ready for GUI: {payload.get('ready_for_gui')}")
    if isinstance(summary, dict):
        print(f"  Errors: {summary.get('error_count', 0)}")
        print(f"  Warnings: {summary.get('warning_count', 0)}")
        print(f"  Assets: {summary.get('asset_count', 0)}")
    print(f"  Next action: {payload.get('next_action')}")


def _print_workspace_text(payload: dict[str, object]) -> None:
    print("GUI workspace state")
    print(f"  Active page: {payload.get('active_page_id')}")
    print(f"  Workspace root: {payload.get('workspace_root')}")
    recent = payload.get("recent_counts", {})
    if isinstance(recent, dict):
        print(f"  Recent people bundles: {recent.get('people_bundle_dirs', 0)}")


def _print_command_plan_text(payload: dict[str, object]) -> None:
    print("GUI command plan")
    print(f"  ID: {payload.get('plan_id')}")
    print(f"  Title: {payload.get('title')}")
    print(f"  Enabled: {payload.get('enabled')}")
    print(f"  Risk: {payload.get('risk_level')}")
    print(f"  Command: {payload.get('command_preview')}")


def _print_desktop_runtime_text(payload: dict[str, object]) -> None:
    print(summarize_gui_desktop_runtime_state(payload))
    if payload.get("output_dir"):
        print(f"  Output dir: {payload.get('output_dir')}")
        print(f"  Written files: {payload.get('written_file_count')}")


def _print_ui_view_models_text(payload: dict[str, object]) -> None:
    print(summarize_ui_app_service_view_models(payload))
    if payload.get("output_dir"):
        print(f"  Output dir: {payload.get('output_dir')}")
        print(f"  Written files: {payload.get('written_file_count')}")


def _emit(payload: dict[str, object], *, out: Path | None, json_output: bool, text_printer) -> None:
    if out is not None:
        write_json_object(out, payload)
    if json_output:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        text_printer(payload)


def _workspace_summary_payload(state: dict[str, object]) -> dict[str, object]:
    return {**state, **build_gui_state_summary(state)}


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    command = args.service_command or "home-state"

    if command == "home-state":
        payload = build_app_home_state(
            profile_dir=args.profile_dir,
            run_dir=args.run_dir,
            people_bundle_dir=args.people_bundle_dir,
            active_page_id=args.active_page,
            run_limit=args.run_limit,
        )
        _emit(payload, out=args.out, json_output=args.json, text_printer=_print_home_text)
        return 0

    if command == "startup-state":
        payload = build_app_startup_state(
            gui_state_path=args.gui_state,
            profile_dir=args.profile_dir,
            run_dir=args.run_dir,
            people_bundle_dir=args.people_bundle_dir,
            active_page_id=args.active_page,
        )
        _emit(payload, out=args.out, json_output=args.json, text_printer=_print_home_text)
        return 0

    if command == "desktop-runtime":
        try:
            if args.out_dir is not None:
                payload = write_gui_desktop_runtime_state(
                    args.out_dir,
                    profile_dir=args.profile_dir,
                    run_dir=args.run_dir,
                    people_bundle_dir=args.people_bundle_dir,
                    active_page_id=args.active_page,
                    home_state_json=args.home_state_json,
                    settings_json=args.settings_json,
                    view_state_json=args.view_state_json,
                    language=args.language,
                    theme=args.theme,
                    density=args.density,
                )
            else:
                payload = build_gui_desktop_runtime_state(
                    profile_dir=args.profile_dir,
                    run_dir=args.run_dir,
                    people_bundle_dir=args.people_bundle_dir,
                    active_page_id=args.active_page,
                    home_state_json=args.home_state_json,
                    settings_json=args.settings_json,
                    view_state_json=args.view_state_json,
                    language=args.language,
                    theme=args.theme,
                    density=args.density,
                )
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            parser.error(str(exc))
        _emit(payload, out=args.out, json_output=args.json, text_printer=_print_desktop_runtime_text)
        return 0 if payload.get("readiness", {}).get("ready") else 2

    if command == "ui-view-models":
        try:
            if args.out_dir is not None:
                payload = write_ui_app_service_view_models(
                    args.out_dir,
                    profile_dir=args.profile_dir,
                    run_dir=args.run_dir,
                    people_bundle_dir=args.people_bundle_dir,
                    active_page_id=args.active_page,
                    home_state_json=args.home_state_json,
                    language=args.language,
                )
            else:
                payload = build_ui_app_service_view_models(
                    profile_dir=args.profile_dir,
                    run_dir=args.run_dir,
                    people_bundle_dir=args.people_bundle_dir,
                    active_page_id=args.active_page,
                    home_state_json=args.home_state_json,
                    language=args.language,
                )
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            parser.error(str(exc))
        _emit(payload, out=args.out, json_output=args.json, text_printer=_print_ui_view_models_text)
        return 0

    if command == "report-bundle":
        try:
            report_payload = read_json_object(args.report_json)
            command_payload = read_json_object(args.command_json) if args.command_json is not None else None
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            parser.error(str(exc))
        payload = write_report_service_bundle(
            args.out_dir,
            command_name=args.command,
            report_payload=report_payload,
            command_payload=command_payload,
            run_id=args.run_id,
            entry_limit=args.entry_limit,
        )
        _emit(payload, out=None, json_output=args.json, text_printer=_print_report_bundle_text)
        return 0

    if command == "pages":
        payload = {"catalog": build_gui_page_catalog(), "navigation": build_gui_navigation_state(args.active_page)}
        _emit(payload, out=args.out, json_output=args.json, text_printer=_print_pages_text)
        return 0

    if command == "workspace":
        workspace_command = args.workspace_command or "show"
        if workspace_command == "init":
            if args.state_json.exists() and not args.overwrite:
                parser.error(f"GUI state already exists: {args.state_json}")
            state = build_default_gui_state(workspace_root=args.workspace_root)
            write_gui_state(args.state_json, state)
            payload = _workspace_summary_payload(state)
            _emit(payload, out=None, json_output=args.json, text_printer=_print_workspace_text)
            return 0
        try:
            state = load_gui_state(args.state_json)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            parser.error(str(exc))
        if workspace_command == "show":
            payload = _workspace_summary_payload(state)
            _emit(payload, out=None, json_output=args.json, text_printer=_print_workspace_text)
            return 0
        if workspace_command == "set-page":
            state = set_active_page(state, args.page_id)
        elif workspace_command == "add-recent":
            state = add_recent_path(state, section=args.section, path=args.path)
        elif workspace_command == "register-people-bundle":
            state = register_people_bundle(state, bundle_dir=args.bundle_dir, catalog_path=args.catalog)
        else:
            parser.error(f"Unsupported workspace command: {workspace_command}")
        write_gui_state(args.state_json, state)
        payload = _workspace_summary_payload(state)
        _emit(payload, out=None, json_output=args.json, text_printer=_print_workspace_text)
        return 0

    if command == "people-review-preview":
        try:
            workflow_payload = read_json_object(args.workflow_json)
            report_payload = read_json_object(args.report_json)
            payload = build_people_review_apply_preview(
                catalog_path=args.catalog,
                workflow_payload=workflow_payload,
                report_payload=report_payload,
                output_catalog_path=args.out_catalog,
            )
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            parser.error(str(exc))
        if args.out is not None:
            write_people_review_apply_preview(args.out, payload)
        if args.json:
            print(json.dumps(payload, indent=2, ensure_ascii=False))
        else:
            _print_preview_text(payload)
        return 0 if payload.get("status") == "ok" else 1

    if command == "validate-people-bundle":
        payload = validate_people_review_bundle(args.bundle_dir)
        if args.out is not None:
            write_people_review_bundle_validation(args.out, payload)
        if args.json:
            print(json.dumps(payload, indent=2, ensure_ascii=False))
        else:
            _print_validation_text(payload)
        return 0 if payload.get("status") == "ok" else 1

    if command == "command-plan":
        plan_command = args.plan_command or "profile"
        try:
            if plan_command == "profile":
                payload = build_profile_command_plan(args.profile)
            elif plan_command == "people-review-apply":
                payload = build_people_review_apply_command_plan(
                    catalog_path=args.catalog,
                    workflow_json=args.workflow_json,
                    report_json=args.report_json,
                    out_catalog=args.out_catalog,
                    dry_run=args.dry_run,
                )
            elif plan_command == "open-people-bundle":
                payload = build_open_people_bundle_plan(args.bundle_dir)
            else:
                parser.error(f"Unsupported command-plan command: {plan_command}")
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            parser.error(str(exc))
        if args.out is not None:
            write_command_plan(args.out, payload)
        if args.json:
            print(json.dumps(payload, indent=2, ensure_ascii=False))
        else:
            _print_command_plan_text(payload)
        return 0 if payload.get("enabled", True) else 1

    parser.error(f"Unsupported app service command: {command}")
    return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
