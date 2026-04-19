# Hotfix: workflow last --json compatibility

Problem:
`media-manager workflow last --json` now returns a wrapped payload, so older callers/tests
that expect `command_name` at the top level fail.

Required fix:
In `src/media_manager/cli_workflow.py`, change the **successful JSON branch** of the
`last` command so that the entry fields stay at the top level.

Apply this logic in the success branch:

```python
payload = _history_payload(entry)
payload["command_filter"] = command_name
payload["record_type_filter"] = getattr(args, "record_type", None)
payload["only_successful"] = bool(getattr(args, "only_successful", False))
payload["only_failed"] = bool(getattr(args, "only_failed", False))
payload["only_apply"] = bool(getattr(args, "only_apply", False))
payload["only_preview"] = bool(getattr(args, "only_preview", False))
payload["has_reversible_entries"] = bool(getattr(args, "has_reversible_entries", False))
payload["min_entry_count"] = getattr(args, "min_entry_count", None)
payload["min_reversible_entry_count"] = getattr(args, "min_reversible_entry_count", None)
print(json.dumps(payload, indent=2, ensure_ascii=False))
return 0
```

Important:
Do **not** nest the entry under `"entry"` on the successful JSON path.
Keep `command_name`, `path`, `record_type`, `exit_code`, etc. at the top level.
Extra filter metadata can be added additively, but the old keys must remain top-level.

This preserves backward compatibility with existing tests like:
- `tests/test_cli_workflow_history_v2.py::test_cli_workflow_last_json_output_filters_by_command`
