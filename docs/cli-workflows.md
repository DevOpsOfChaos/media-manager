# Workflow CLI guide

This document summarizes the current workflow-oriented CLI surface.

The workflow layer is designed to sit on top of the lower-level media commands. It helps users:

- discover available workflows
- choose a good starting point
- save repeatable profile configurations
- inventory and audit those profiles
- export and reuse them as bundles
- execute profiles or bundle selections in batches

## Discovery

```powershell
media-manager workflow list
media-manager workflow show cleanup
media-manager workflow problems
media-manager workflow recommend messy-multi-source-library
media-manager workflow wizard --source-count 3 --has-duplicates --wants-organization
```

## Presets

Presets are reusable built-in workflow starting points.

```powershell
media-manager workflow presets
media-manager workflow preset-show cleanup-family-library
media-manager workflow render-preset cleanup-family-library --source C:\Photos --source D:\Phone --target E:\Library
```

## Profiles

Profiles are saved JSON files built from presets plus chosen values.

```powershell
media-manager workflow profile-save .\profiles\family-cleanup.json --preset cleanup-family-library --source C:\Photos --source D:\Phone --target E:\Library
media-manager workflow profile-show .\profiles\family-cleanup.json
media-manager workflow profile-validate .\profiles\family-cleanup.json
media-manager workflow profile-run .\profiles\family-cleanup.json --show-command
```

### Profile directory commands

```powershell
media-manager workflow profile-list --profiles-dir .\profiles
media-manager workflow profile-audit --profiles-dir .\profiles
media-manager workflow profile-run-dir --profiles-dir .\profiles --only-valid
```

Useful filters:

- `--workflow <NAME>`
- `--preset <NAME>`
- `--profile-name-contains <TEXT>`
- `--profile-path-contains <TEXT>`
- `--only-valid`
- `--only-invalid`
- `--show-command`
- `--summary-only`
- `--continue-on-error`
- `--fail-on-empty`
- `--json`

### Profile selection filters

The profile directory commands can now narrow large profile collections without forcing you to reorganize files first.

Examples:

```powershell
media-manager workflow profile-list --profiles-dir .\profiles --profile-name-contains family
media-manager workflow profile-audit --profiles-dir .\profiles --profile-path-contains family\
media-manager workflow profile-run-dir --profiles-dir .\profiles --profile-name-contains cleanup --only-valid
```

`--profile-path-contains` is path-normalized. Slash and backslash variants are treated the same so the filter stays usable on Windows.

## Profile bundles

Bundles are portable JSON snapshots of profile collections.

### Write / inspect / audit

```powershell
media-manager workflow profile-bundle-write .\bundles\profiles.json --profiles-dir .\profiles
media-manager workflow profile-bundle-show .\bundles\profiles.json
media-manager workflow profile-bundle-audit .\bundles\profiles.json
```

### Merge / compare

```powershell
media-manager workflow profile-bundle-merge .\bundles\merged.json .\bundles\team-a.json .\bundles\team-b.json --prefer last
media-manager workflow profile-bundle-compare .\bundles\before.json .\bundles\after.json --only-changed
```

### Extract / sync / run

```powershell
media-manager workflow profile-bundle-extract .\bundles\profiles.json --target-dir .\profiles-restored
media-manager workflow profile-bundle-sync .\bundles\profiles.json --target-dir .\profiles-restored --apply
media-manager workflow profile-bundle-run .\bundles\profiles.json --only-valid
```

### Bundle directory commands

```powershell
media-manager workflow profile-bundle-list-dir --bundles-dir .\bundles
media-manager workflow profile-bundle-audit-dir --bundles-dir .\bundles
media-manager workflow profile-bundle-run-dir --bundles-dir .\bundles --only-clean-bundles
```

### Bundle selection filters

Bundle-oriented commands support the same kind of narrowing at the bundle layer.

Examples:

```powershell
media-manager workflow profile-bundle-write .\bundles\family.json --profiles-dir .\profiles --profile-name-contains family --profile-path-contains family\
media-manager workflow profile-bundle-show .\bundles\profiles.json --relative-path-contains trips\
media-manager workflow profile-bundle-list-dir --bundles-dir .\bundles --profile-name-contains family
```

Useful filters:

- `--workflow <NAME>`
- `--preset <NAME>`
- `--profile-name-contains <TEXT>`
- `--relative-path-contains <TEXT>`
- `--only-valid`
- `--only-invalid`
- `--only-clean-bundles`
- `--only-problematic-bundles`
- `--show-command`
- `--summary-only`
- `--continue-on-error`
- `--fail-on-empty`
- `--json`

## History

Workflow history sits next to the workflow/profile layer and helps with repeatable review.

### Basic history views

```powershell
media-manager workflow history --path .\runs
media-manager workflow history --path .\runs --command organize
media-manager workflow last --path .\runs --command organize
media-manager workflow history-latest-by-command --path .\runs --only-failed --summary-only
```

### History audit filters

The history commands support stronger audit-style filtering.

```powershell
media-manager workflow history --path .\runs --command organize --record-type run_log --only-failed
media-manager workflow history --path .\runs --only-apply --has-reversible-entries --min-entry-count 10 --summary-only
media-manager workflow last --path .\runs --command trip --record-type execution_journal --only-successful
```

Useful history filters:

- `--record-type <run_log|execution_journal>`
- `--only-successful`
- `--only-failed`
- `--only-apply`
- `--only-preview`
- `--has-reversible-entries`
- `--min-entry-count <N>`
- `--min-reversible-entry-count <N>`
- `--created-at-after <ISO_TIMESTAMP>`
- `--created-at-before <ISO_TIMESTAMP>`
- `--summary-only` on `history` and `history-latest-by-command`
- `--fail-on-empty` on `history` and `history-latest-by-command`

### Date-window examples

```powershell
media-manager workflow history --path .\runs --created-at-after 2026-04-01T00:00:00Z --created-at-before 2026-04-30T23:59:59Z
media-manager workflow last --path .\runs --command organize --created-at-after 2026-04-15T00:00:00Z
media-manager workflow history-latest-by-command --path .\runs --created-at-after 2026-04-01T00:00:00Z --only-successful
```

### Audit snapshot direction

The core history layer also supports a richer audit snapshot view that combines:

- the filtered overall summary
- the newest matching entry per command
- per-command summary rows

That makes it a good building block for later workflow reporting surfaces without rewriting audit logic in multiple places.

See also:

- `docs/workflow-history.md`
- `docs/workflow-profiles-and-bundles.md`

## Notes

- Windows is the primary target right now.
- English is the primary language for CLI output and JSON fields.
- Prefer preview/review flows before destructive apply modes.
- The workflow layer is meant to make the lower-level CLI more repeatable, not to hide it completely.
