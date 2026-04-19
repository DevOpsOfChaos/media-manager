# Fix für `history-summary-by-command`

Dein Testfehler ist sauber eingegrenzt:

- `tests/test_cli_workflow_history_summary_by_command_v1.py` ist vorhanden
- aber `src/media_manager/cli_workflow.py` kennt den neuen Subcommand noch nicht

Darum kommt nur:

`invalid choice: 'history-summary-by-command'`

## Betroffene Datei

- `src/media_manager/cli_workflow.py`

## 1) Import erweitern

Im Import aus `.core.state` zusätzlich `summarize_history_entries_by_command` ergänzen.

```python
from .core.state import (
    build_history_summary,
    find_latest_history_entries_by_command,
    find_latest_history_entry,
    scan_history_directory,
    summarize_history_entries_by_command,
)
```

## 2) Parser ergänzen

Direkt nach `history-latest-by-command` ergänzen:

```python
    history_summary_by_command_parser = subparsers.add_parser(
        "history-summary-by-command",
        help="Show aggregated workflow history summary rows grouped by command.",
    )
    history_summary_by_command_parser.add_argument(
        "--path",
        type=Path,
        required=True,
        help="Directory to scan for run logs and journals.",
    )
    _add_history_filter_arguments(
        history_summary_by_command_parser,
        include_summary_only=True,
        include_fail_on_empty=True,
    )
    history_summary_by_command_parser.add_argument(
        "--json",
        action="store_true",
        help="Print JSON output.",
    )
```

## 3) Payload-Helfer ergänzen

Direkt nach `_history_payload(...)` einfügen:

```python
def _history_command_summary_payload(item) -> dict[str, object]:
    return item.to_dict()
```

## 4) Handler ergänzen

Direkt nach `_print_history_latest_by_command(...)` einfügen:

```python
def _print_history_summary_by_command(args: argparse.Namespace) -> int:
    filter_kwargs = _build_history_filter_kwargs(args)
    filter_payload = _build_history_filter_payload(args)
    filtered_entries = scan_history_directory(args.path, **filter_kwargs)
    summary = build_history_summary(filtered_entries)
    command_summaries = summarize_history_entries_by_command(filtered_entries)
    payload = {
        "path": str(args.path),
        **filter_payload,
        "summary_only": bool(getattr(args, "summary_only", False)),
        "summary": summary,
        "command_summaries": []
        if getattr(args, "summary_only", False)
        else [_history_command_summary_payload(item) for item in command_summaries],
    }
    exit_code = 1 if getattr(args, "fail_on_empty", False) and not command_summaries else 0
    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return exit_code

    lines = [f"Workflow history summary by command in {args.path}"]
    _append_history_filter_lines(lines, args)
    lines.extend(
        [
            f"  Commands matched: {len(command_summaries)}",
            f"  Total entries: {summary['entry_count']}",
            f"  Successful: {summary['successful_count']}",
            f"  Failed: {summary['failed_count']}",
            f"  Reversible entries: {summary['reversible_entry_count']}",
            f"  Entries with reversible actions: {summary['entries_with_reversible_count']}",
        ]
    )
    if summary["latest_created_at_utc"]:
        lines.append(f"  Latest: {summary['latest_created_at_utc']}")
    if summary["apply_summary"]:
        apply_text = ", ".join(f"{key}={value}" for key, value in summary["apply_summary"].items())
        lines.append(f"  Apply modes: {apply_text}")
    if summary["exit_code_summary"]:
        exit_text = ", ".join(f"{key}={value}" for key, value in summary["exit_code_summary"].items())
        lines.append(f"  Exit codes: {exit_text}")
    if not command_summaries:
        lines.append("  No recognized run logs or execution journals found.")
        print("\n".join(lines))
        return exit_code
    if summary["command_summary"]:
        command_text = ", ".join(f"{key}={value}" for key, value in summary["command_summary"].items())
        lines.append(f"  Commands: {command_text}")
    if summary["record_type_summary"]:
        record_text = ", ".join(f"{key}={value}" for key, value in summary["record_type_summary"].items())
        lines.append(f"  Record types: {record_text}")
    if getattr(args, "summary_only", False):
        print("\n".join(lines))
        return exit_code
    for item in command_summaries:
        lines.append(
            f"  - {item.command_name} | runs={item.entry_count} | successful={item.successful_count} | "
            f"failed={item.failed_count} | latest={item.latest_created_at_utc}"
        )
        lines.append(
            f"    latest: type={item.latest_record_type} | apply={item.latest_apply_requested} | "
            f"exit={item.latest_exit_code} | entries={item.latest_entry_count} | "
            f"reversible={item.latest_reversible_entry_count}"
        )
        lines.append(
            f"    totals: apply={item.apply_requested_count} | preview={item.preview_only_count} | "
            f"reversible_entries={item.reversible_entry_count} | "
            f"entries_with_reversible={item.entries_with_reversible_count}"
        )
        if item.record_type_summary:
            record_text = ", ".join(f"{key}={value}" for key, value in item.record_type_summary.items())
            lines.append(f"    record types: {record_text}")
        if item.exit_code_summary:
            exit_text = ", ".join(f"{key}={value}" for key, value in item.exit_code_summary.items())
            lines.append(f"    exit codes: {exit_text}")
        if item.latest_path:
            lines.append(f"    {item.latest_path}")
    print("\n".join(lines))
    return exit_code
```

## 5) Hilfe-Text ergänzen

Im großen Hilfe-Block in `main(...)` ergänzen:

```python
            "  media-manager workflow history-summary-by-command --path <RUNS_DIR> --summary-only\n"
```

## 6) Dispatch ergänzen

Direkt nach `history-latest-by-command`:

```python
    if args.workflow_command == "history-summary-by-command":
        return _print_history_summary_by_command(args)
```
