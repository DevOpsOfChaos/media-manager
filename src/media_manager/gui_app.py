from __future__ import annotations

import argparse
import json
from pathlib import Path

from .core.gui_shell_model import build_gui_shell_model_from_paths, summarize_gui_shell_model
from .gui_desktop_tk import run_tk_gui


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="media-manager-gui",
        description="Launch or inspect the lightweight Media Manager desktop GUI shell.",
    )
    parser.add_argument("--active-page", default="dashboard", help="Initial GUI page id. Default: dashboard.")
    parser.add_argument("--profile-dir", type=Path, help="Optional app profile directory.")
    parser.add_argument("--run-dir", type=Path, help="Optional run artifact root.")
    parser.add_argument("--people-bundle-dir", type=Path, help="Optional people review bundle directory.")
    parser.add_argument("--home-state-json", type=Path, help="Optional prebuilt app home-state JSON.")
    parser.add_argument("--json", action="store_true", help="Print the GUI shell model as JSON and do not open a window.")
    parser.add_argument("--summary", action="store_true", help="Print a compact GUI shell summary and do not open a window.")
    parser.add_argument("--no-window", action="store_true", help="Build the shell model without opening a GUI window.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        model = build_gui_shell_model_from_paths(
            profile_dir=args.profile_dir,
            run_dir=args.run_dir,
            people_bundle_dir=args.people_bundle_dir,
            active_page_id=args.active_page,
            home_state_json=args.home_state_json,
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))

    if args.json:
        print(json.dumps(model, indent=2, ensure_ascii=False))
        return 0
    if args.summary or args.no_window:
        print(summarize_gui_shell_model(model))
        return 0
    return run_tk_gui(model)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
