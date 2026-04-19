# Workflow History JSON Contracts

This document describes the practical JSON compatibility rules for the workflow history surface.

It exists because the workflow history layer now has several related commands with different output shapes:

- `media-manager workflow history`
- `media-manager workflow last`
- `media-manager workflow history-latest-by-command`

The goal is simple:

- keep existing machine-readable fields stable
- only extend payloads additively
- make it obvious which fields are command-specific
- reduce accidental regressions when new filters or summary helpers are added

## General rules

When extending workflow history JSON output:

1. Do not silently rename existing fields.
2. Do not move previously top-level fields into nested objects.
3. Add new metadata as new fields rather than changing old ones.
4. Keep path fields explicit when both a history root path and an entry file path are relevant.
5. Prefer the same filter field names across commands where possible.

## `workflow history --json`

The `history` command returns a collection payload.

Expected structure:

- `path`
- history filter metadata such as `command_filter`
- `summary_only`
- `summary`
- `entries`

`entries` is a list of history-entry payloads.

A history-entry payload currently includes:

- `path`
- `record_type`
- `command_name`
- `apply_requested`
- `exit_code`
- `created_at_utc`
- `entry_count`
- `reversible_entry_count`
- `successful`
- `has_reversible_entries`

## `workflow last --json`

The `last` command is compatibility-sensitive.

The current practical contract should be treated as deliberate:

- top-level entry fields remain directly accessible
- `entry` also contains the selected entry payload
- `path` refers to the requested history root path
- `entry_path` refers to the concrete matched entry file
- filter metadata is additive

That means downstream users may legitimately depend on both of these styles:

- `payload["command_name"]`
- `payload["entry"]["command_name"]`

Do not remove either form without a planned compatibility change.

## `workflow history-latest-by-command --json`

This command is a grouped collection payload.

Expected structure:

- `path`
- history filter metadata
- `summary_only`
- `summary`
- `entries`

`entries` is a list of regular history-entry payloads, one per command, already reduced to the newest matching entry for each command.

This command should stay additive and must not change the established `history` or `last` payload contracts.

## Filter metadata naming

The workflow history CLI uses these JSON-facing filter metadata fields:

- `command_filter`
- `record_type_filter`
- `only_successful`
- `only_failed`
- `only_apply_requested`
- `only_preview`
- `has_reversible_entries`
- `min_entry_count`
- `min_reversible_entry_count`
- `created_at_after`
- `created_at_before`

For compatibility, new commands should reuse these names instead of inventing command-local variants.

## Path naming guidance

When JSON needs to describe both the scan root and a specific matched file, keep them separate.

Recommended naming:

- `path` for the requested root directory when that is already established behavior
- `entry_path` for one matched file
- `entries[*].path` for list-style entry payloads

Do not overload one field to mean both things.

## Summary guidance

Collection commands may include a `summary` object.

When adding new summary fields:

- preserve existing counts
- prefer additive nested fields
- keep `entry_count` stable if users already depend on it

## Regression checklist

Before changing workflow history JSON:

1. Run the focused history JSON tests first.
2. Run the broader workflow CLI tests.
3. Run the full test suite.
4. Inspect whether a new field can be added instead of reshaping existing output.
5. Check for compatibility-sensitive path handling on Windows.

## Why this matters

This repository is intentionally building a reusable CLI/core layer first.

That makes JSON output part of the real product surface rather than incidental debug output.

Stable machine-readable history output helps with:

- future GUI integration
- scripting around review and audit flows
- repeatable regression tests
- safer expansion of workflow diagnostics over time
