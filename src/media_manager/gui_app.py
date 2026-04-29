from __future__ import annotations

import argparse
import json
from pathlib import Path

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
from .core.gui_i18n import SUPPORTED_LANGUAGES
from .core.gui_shell_model import build_gui_shell_model_from_paths, summarize_gui_shell_model
from .core.gui_theme import SUPPORTED_THEMES
from .gui_desktop_qt import (
    MissingQtDependencyError,
    attach_guarded_qt_runtime_smoke_to_shell_model,
    build_guarded_qt_runtime_smoke_plan,
    guarded_qt_runtime_smoke_plan_to_pretty_json,
    qt_install_guidance,
    run_qt_gui,
    summarize_guarded_qt_runtime_smoke_plan,
)

DENSITY_CHOICES = ("compact", "comfortable", "spacious")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="media-manager-gui",
        description="Launch or inspect the modern Media Manager desktop GUI shell.",
    )
    parser.add_argument("--active-page", default="dashboard", help="Initial GUI page id. Default: dashboard.")
    parser.add_argument("--profile-dir", type=Path, help="Optional app profile directory.")
    parser.add_argument("--run-dir", type=Path, help="Optional run artifact root.")
    parser.add_argument("--people-bundle-dir", type=Path, help="Optional people review bundle directory.")
    parser.add_argument("--home-state-json", type=Path, help="Optional prebuilt app home-state JSON.")
    parser.add_argument("--settings-json", type=Path, help="Optional GUI settings JSON.")
    parser.add_argument("--view-state-json", type=Path, help="Optional GUI view-state JSON.")
    parser.add_argument("--language", choices=SUPPORTED_LANGUAGES, help="GUI language. Supported: en, de.")
    parser.add_argument("--theme", choices=SUPPORTED_THEMES, help="GUI theme. Default comes from settings or modern-dark.")
    parser.add_argument("--density", choices=DENSITY_CHOICES, help="GUI density. Default comes from settings or comfortable.")
    parser.add_argument("--json", action="store_true", help="Print the GUI shell model as JSON and do not open a window.")
    parser.add_argument("--summary", action="store_true", help="Print a compact GUI shell summary and do not open a window.")
    parser.add_argument("--no-window", action="store_true", help="Build the shell model without opening a GUI window.")
    parser.add_argument("--desktop-runtime-json", action="store_true", help="Print the headless desktop runtime state consumed by the future Qt UI and do not open a window.")
    parser.add_argument("--desktop-runtime-summary", action="store_true", help="Print a compact desktop runtime readiness summary and do not open a window.")
    parser.add_argument("--desktop-runtime-out-dir", type=Path, help="Write split desktop runtime JSON files to this directory and do not open a window.")
    parser.add_argument("--ui-view-models-json", action="store_true", help="Print product UI app-service view models as JSON and do not open a window.")
    parser.add_argument("--ui-view-models-summary", action="store_true", help="Print a compact product UI app-service view-model summary and do not open a window.")
    parser.add_argument("--ui-view-models-out-dir", type=Path, help="Write split product UI app-service view-model JSON files to this directory and do not open a window.")
    parser.add_argument("--runtime-smoke-json", action="store_true", help="Print the guarded Runtime Smoke integration as JSON and do not open a window.")
    parser.add_argument("--runtime-smoke-summary", action="store_true", help="Print a guarded Runtime Smoke summary and do not open a window.")
    parser.add_argument("--check-backend", action="store_true", help="Check whether the modern Qt backend can be imported.")
    return parser


def build_model_from_args(args: argparse.Namespace) -> dict[str, object]:
    return build_gui_shell_model_from_paths(
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


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.check_backend:
        try:
            from .gui_desktop_qt import load_qt_modules

            load_qt_modules()
        except MissingQtDependencyError:
            print(qt_install_guidance())
            return 1
        print("Modern Qt backend is available.")
        return 0

    try:
        model = build_model_from_args(args)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))

    runtime_smoke_active = str(args.active_page or "").strip().lower().replace("_", "-") == "runtime-smoke"
    if runtime_smoke_active:
        model = attach_guarded_qt_runtime_smoke_to_shell_model(model, activate=True)

    if args.ui_view_models_out_dir:
        try:
            payload = write_ui_app_service_view_models(
                args.ui_view_models_out_dir,
                profile_dir=args.profile_dir,
                run_dir=args.run_dir,
                people_bundle_dir=args.people_bundle_dir,
                active_page_id=args.active_page,
                home_state_json=args.home_state_json,
                language=args.language,
            )
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            parser.error(str(exc))
        print(summarize_ui_app_service_view_models(payload))
        print(f"  Output dir: {payload['output_dir']}")
        print(f"  Written files: {payload['written_file_count']}")
        return 0
    if args.ui_view_models_json or args.ui_view_models_summary:
        try:
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
        if args.ui_view_models_json:
            print(json.dumps(payload, indent=2, ensure_ascii=False))
        else:
            print(summarize_ui_app_service_view_models(payload))
        return 0
    if args.desktop_runtime_out_dir:
        try:
            payload = write_gui_desktop_runtime_state(
                args.desktop_runtime_out_dir,
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
        print(summarize_gui_desktop_runtime_state(payload))
        print(f"  Output dir: {payload['output_dir']}")
        print(f"  Written files: {payload['written_file_count']}")
        return 0 if payload.get("readiness", {}).get("ready") else 2
    if args.desktop_runtime_json or args.desktop_runtime_summary:
        try:
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
        if args.desktop_runtime_json:
            print(json.dumps(payload, indent=2, ensure_ascii=False))
        else:
            print(summarize_gui_desktop_runtime_state(payload))
        return 0 if payload.get("readiness", {}).get("ready") else 2
    if args.runtime_smoke_json:
        print(guarded_qt_runtime_smoke_plan_to_pretty_json(model))
        return 0
    if args.runtime_smoke_summary:
        print(summarize_guarded_qt_runtime_smoke_plan(model))
        return 0
    if args.json:
        print(json.dumps(model, indent=2, ensure_ascii=False))
        return 0
    if args.summary or args.no_window:
        if runtime_smoke_active:
            print(summarize_guarded_qt_runtime_smoke_plan(model))
        else:
            print(summarize_gui_shell_model(model))
        return 0
    try:
        return run_qt_gui(model)
    except MissingQtDependencyError:
        print(qt_install_guidance())
        return 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
