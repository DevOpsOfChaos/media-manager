# Cleanup Workflow v1

## Goal

Provide a guided dry-run workflow for the common real-world cleanup case:

- several messy source folders
- likely exact duplicates
- a planned organize target
- a planned rename strategy

The cleanup workflow does **not** execute everything automatically.
It combines the existing core planners into one reviewable report.

## Command

```powershell
media-manager cleanup --source <DIR_A> --source <DIR_B> --target <TARGET>
```

## Included sections

The workflow currently combines:

1. scan summary
2. exact duplicate scan and optional keep-policy decisions
3. organize dry-run summary
4. rename dry-run summary

## Duplicate options

- `--duplicate-policy first|newest|oldest`
- `--duplicate-mode copy|move|delete`

If a duplicate policy is supplied, the workflow also builds the duplicate cleanup plan section.

## Organize options

- `--organize-pattern`

This pattern is passed through to the existing organize dry-run planner.

## Rename options

- `--rename-template`

This template is passed through to the existing rename dry-run planner.

## Output modes

- normal human-readable summary
- `--show-files` for per-entry details
- `--json` for machine-readable output
- `--run-log <PATH>` for a persistent command log

## Why this exists

This is the first workflow that connects multiple rebuilt subsystems into one practical user-facing problem flow.

It is intentionally conservative:

- no global apply button
- no hidden destructive behavior
- no fake automation pretending to solve unresolved duplicate decisions

It is a guided report layer built on top of the real core modules.
