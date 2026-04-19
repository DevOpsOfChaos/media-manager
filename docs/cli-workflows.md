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

```powershell
media-manager workflow history --path .\runs
media-manager workflow history --path .\runs --command organize
media-manager workflow last --path .\runs --command organize
```

## Notes

- Windows is the primary target right now.
- English is the primary language for CLI output and JSON fields.
- Prefer preview/review flows before destructive apply modes.
- The workflow layer is meant to make the lower-level CLI more repeatable, not to hide it completely.
