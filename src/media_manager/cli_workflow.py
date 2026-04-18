from __future__ import annotations

import argparse
import json

from . import cli_duplicates, cli_organize, cli_rename, cli_trip

try:  # optional while older cumulative states are still present
    from . import cli_cleanup
except Exception:  # pragma: no cover - compatibility fallback
    cli_cleanup = None

from .core.workflows import (
    build_workflow_wizard_result,
    get_workflow_definition,
    get_workflow_problem,
    list_workflow_problems,
    list_workflows,
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

    run_parser = subparsers.add_parser("run", help="Run a workflow through the shell.")
    run_parser.add_argument("workflow", help="Workflow name to run.")
    run_parser.add_argument("args", nargs=argparse.REMAINDER, help="Arguments forwarded to the delegated workflow.")
    return parser


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
    if args.workflow_command == "run":
        return _run_delegated_workflow(args.workflow, list(args.args))

    parser.print_help()
    return 2
