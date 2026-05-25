from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from . import (
    cli_app,
    cli_cleanup,
    cli_duplicates,
    cli_doctor,
    cli_inspect,
    cli_organize,
    cli_people,
    cli_rename,
    cli_runs,
    cli_trip,
    cli_undo,
    cli_workflow,
)


def _setup_logging() -> None:
    log_dir = Path.home() / ".media-manager" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(log_dir / "app.log", encoding="utf-8"),
            logging.StreamHandler(),  # also print to stderr
        ],
    )
    logging.getLogger("PIL").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)


COMMAND_HANDLERS = {
    "app": cli_app.main,
    "cleanup": cli_cleanup.main,
    "duplicates": cli_duplicates.main,
    "doctor": cli_doctor.main,
    "inspect": cli_inspect.main,
    "organize": cli_organize.main,
    "people": cli_people.main,
    "rename": cli_rename.main,
    "runs": cli_runs.main,
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
    parser.epilog = (
        "Examples:\n"
        "  media-manager organize --source ~/Photos --target ~/Organized\n"
        "  media-manager duplicates --source ~/Photos\n"
        "  media-manager people scan --source ~/Photos --catalog catalog.json\n"
        "  media-manager trip --source ~/Photos --label \"Italy 2024\"\n"
        "\n"
        "For detailed help on a subcommand:\n"
        "  media-manager <subcommand> --help"
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    if "--version" in sys.argv or "-V" in sys.argv:
        from . import __version__
        print(f"media-manager v{__version__}")
        return 0

    _setup_logging()
    argv = list(sys.argv[1:] if argv is None else argv)
    parser = build_parser()

    if not argv:
        parser.print_help()
        print(
            "\nNo command provided.\n"
            "Run an explicit CLI command such as 'inspect', 'organize', 'rename', 'trip', "
            "'duplicates', 'doctor', 'people', 'runs', 'app', 'undo', 'cleanup', or 'workflow'."
        )
        return 0

    parsed = parser.parse_args(argv)
    if parsed.command is None:
        parser.print_help()
        return 2

    handler = COMMAND_HANDLERS[parsed.command]
    return handler(parsed.args)
