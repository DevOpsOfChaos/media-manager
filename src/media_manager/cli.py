from __future__ import annotations

import argparse
import sys

from . import (
    cli_cleanup,
    cli_duplicates,
    cli_doctor,
    cli_inspect,
    cli_organize,
    cli_rename,
    cli_trip,
    cli_undo,
    cli_workflow,
)


COMMAND_HANDLERS = {
    "cleanup": cli_cleanup.main,
    "duplicates": cli_duplicates.main,
    "doctor": cli_doctor.main,
    "inspect": cli_inspect.main,
    "organize": cli_organize.main,
    "rename": cli_rename.main,
    "trip": cli_trip.main,
    "undo": cli_undo.main,
    "workflow": cli_workflow.main,
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="media-manager",
        description=(
            "Core-first media manager CLI. "
            "Desktop UI entry points were removed from the active repository baseline."
        ),
    )
    parser.add_argument(
        "command",
        nargs="?",
        choices=sorted(COMMAND_HANDLERS.keys()),
        help="Command to run.",
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
            "Run an explicit CLI command such as 'inspect', 'organize', 'rename', 'trip', "
            "'duplicates', 'doctor', 'undo', 'cleanup', or 'workflow'."
        )
        return 0

    parsed = parser.parse_args(argv)
    if parsed.command is None:
        parser.print_help()
        return 2

    handler = COMMAND_HANDLERS[parsed.command]
    return handler(parsed.args)
