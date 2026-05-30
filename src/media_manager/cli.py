from __future__ import annotations

import argparse
import importlib.metadata
import logging
import os
import sys
from pathlib import Path

from . import (
    cli_app,
    cli_cleanup,
    cli_completions,
    cli_config,
    cli_duplicates,
    cli_doctor,
    cli_export,
    cli_file_ops,
    cli_inspect,
    cli_jobs,
    cli_organize,
    cli_people,
    cli_rename,
    cli_review,
    cli_runs,
    cli_stats,
    cli_trip,
    cli_undo,
    cli_watch,
    cli_workflow,
)


def _setup_logging() -> None:
    log_dir = Path.home() / ".media-manager" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    if os.environ.get("MEDIA_MANAGER_LOG_JSON"):
        formatter = logging.Formatter(
            '{"time":"%(asctime)s","level":"%(levelname)s","name":"%(name)s","message":"%(message)s"}'
        )
    else:
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        )

    file_handler = logging.FileHandler(log_dir / "app.log", encoding="utf-8")
    file_handler.setFormatter(formatter)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[file_handler, stream_handler],
    )
    logging.getLogger("PIL").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)


COMMAND_HANDLERS = {
    "app": cli_app.main,
    "cleanup": cli_cleanup.main,
    "completions": cli_completions.main,
    "config": cli_config.main,
    "duplicates": cli_duplicates.main,
    "doctor": cli_doctor.main,
    "export": cli_export.main,
    "file-ops": cli_file_ops.main,
    "inspect": cli_inspect.main,
    "jobs": cli_jobs.main,
    "organize": cli_organize.main,
    "people": cli_people.main,
    "rename": cli_rename.main,
    "review": cli_review.main,
    "runs": cli_runs.main,
    "stats": cli_stats.main,
    "trip": cli_trip.main,
    "undo": cli_undo.main,
    "watch": cli_watch.main,
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
        "--version", "-V",
        action="version",
        version=f"media-manager v{importlib.metadata.version('media-manager')}",
        help="Show the version and exit.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        default=False,
        help="Machine-readable JSON output for all commands.",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        default=False,
        help="Suppress non-error output.",
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
        "  media-manager watch --source ~/Photos --target ~/Organized\n"
        "  media-manager stats --source ~/Photos\n"
        "  media-manager config --show\n"
        "\n"
        "For detailed help on a subcommand:\n"
        "  media-manager <subcommand> --help"
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    _setup_logging()
    argv = list(sys.argv[1:] if argv is None else argv)
    parser = build_parser()

    if not argv:
        parser.print_help()
        print(
            "\nNo command provided.\n"
            "Run an explicit CLI command such as 'inspect', 'organize', 'rename', 'trip', "
            "'duplicates', 'doctor', 'people', 'runs', 'app', 'undo', 'cleanup', 'workflow', "
            "'watch', 'stats', or 'config'.\n"
            "Use 'media-manager <command> --help' for detailed command help."
        )
        return 0

    parsed = parser.parse_args(argv)
    if parsed.command is None:
        parser.print_help()
        if parsed.json or parsed.quiet:
            pass  # flags alone with no command is not an error
        else:
            print(
                "\nHint: Did you forget a command? Available: "
                + ", ".join(sorted(COMMAND_HANDLERS.keys()))
            )
        return 2

    # Propagate global flags to subcommands via environment
    if parsed.json:
        os.environ["MEDIA_MANAGER_JSON"] = "1"
    if parsed.quiet:
        os.environ["MEDIA_MANAGER_QUIET"] = "1"

    handler = COMMAND_HANDLERS[parsed.command]
    return handler(parsed.args)
