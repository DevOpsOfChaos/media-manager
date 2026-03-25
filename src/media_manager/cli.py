from __future__ import annotations

import argparse
import sys

from . import cli_duplicates, cli_gui, cli_organize, cli_rename

COMMAND_HANDLERS = {
    "gui": cli_gui.main,
    "organize": cli_organize.main,
    "duplicates": cli_duplicates.main,
    "rename": cli_rename.main,
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="media-manager")
    parser.add_argument(
        "command",
        nargs="?",
        choices=sorted(COMMAND_HANDLERS.keys()),
        help="Command to run. Leave empty to start the desktop UI.",
    )
    parser.add_argument("args", nargs=argparse.REMAINDER)
    return parser


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv:
        return cli_gui.main()

    parser = build_parser()
    parsed = parser.parse_args(argv)
    if parsed.command is None:
        return cli_gui.main()

    handler = COMMAND_HANDLERS[parsed.command]
    return handler(parsed.args)
