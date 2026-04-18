# Workflow Wizard v1

`media-manager workflow wizard` is the first guided problem-to-workflow helper for the CLI.

It does not replace the real commands.
It helps the user choose the right one.

## Current inputs

- `--problem`
- `--source-count`
- `--has-duplicates`
- `--date-range-known`
- `--wants-trip`
- `--wants-rename`
- `--wants-organization`

## Current outputs

The wizard returns:

- a recommended workflow
- a confidence level
- a short reason
- optional notes
- concrete suggested commands

## Example

```powershell
media-manager workflow wizard --source-count 3 --has-duplicates --wants-organization
```

This typically recommends `cleanup` because that workflow is the safest first overview when multiple sources and duplicate concerns are involved.

## Scope

This is a recommendation layer only.

It does not execute anything on its own.
The actual work still happens through the delegated commands such as:

- `cleanup`
- `trip`
- `duplicates`
- `organize`
- `rename`
