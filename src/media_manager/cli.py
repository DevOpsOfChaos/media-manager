from __future__ import annotations

import argparse
import sys

from . import cli_duplicates, cli_gui, cli_inspect, cli_organize, cli_rename, cli_scan, cli_trip, cli_undo

try:  # optional when older cumulative states are still present
    from . import cli_cleanup
except Exception:  # pragma: no cover - compatibility fallback
    cli_cleanup = None

try:  # optional while the workflow shell is being introduced incrementally
    from . import cli_workflow
except Exception:  # pragma: no cover - compatibility fallback
    cli_workflow = None

COMMAND_HANDLERS = {
    "duplicates": cli_duplicates.main,
    "gui": cli_gui.main,
    "inspect": cli_inspect.main,
    "organize": cli_organize.main,
    "rename": cli_rename.main,
    "scan": cli_scan.main,
    "trip": cli_trip.main,
    "undo": cli_undo.main,
}
if cli_cleanup is not None:
    COMMAND_HANDLERS["cleanup"] = cli_cleanup.main
if cli_workflow is not None:
    COMMAND_HANDLERS["workflow"] = cli_workflow.main


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="media-manager",
        description=(
            "Core-first media manager CLI. "
            "Legacy GUI entry points remain available only when started explicitly."
        ),
    )
    parser.add_argument(
        "command",
        nargs="?",
        choices=sorted(COMMAND_HANDLERS.keys()),
        help=(
            "Command to run. Use 'gui' only if you explicitly want to open the legacy desktop UI."
        ),
    )
    parser.add_argument("args", nargs=argparse.REMAINDER)
    return parser


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    parser = build_parser()

    if not argv:
        parser.print_help()
        print(
            "\nNo command provided.\n"
            "The old default GUI launch behavior has been removed during the repository reset.\n"
            "Run an explicit CLI command such as 'scan', 'inspect', 'organize', 'rename', 'trip', 'duplicates', 'undo', or 'workflow'.\n"
            "Use 'media-manager gui' only if you intentionally want the legacy GUI."
        )
        return 0

    parsed = parser.parse_args(argv)
    if parsed.command is None:
        parser.print_help()
        return 2

    handler = COMMAND_HANDLERS[parsed.command]
    return handler(parsed.args)
