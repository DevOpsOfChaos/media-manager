# Workflow Operations Cheatsheet

This file is a compact command reference for common day-to-day workflow operations.

## Discovery

```powershell
media-manager workflow list
media-manager workflow show cleanup
media-manager workflow problems
media-manager workflow recommend messy-multi-source-library
media-manager workflow wizard --source-count 3 --has-duplicates --wants-organization
```

## Presets

```powershell
media-manager workflow presets
media-manager workflow preset-show cleanup-family-library
media-manager workflow render-preset cleanup-family-library --source C:\Photos --source D:\Phone --target E:\Library
```

## Profiles

### Save and inspect

```powershell
media-manager workflow profile-save .\profiles\family-cleanup.json --preset cleanup-family-library --source C:\Photos --source D:\Phone --target E:\Library
media-manager workflow profile-show .\profiles\family-cleanup.json
media-manager workflow profile-validate .\profiles\family-cleanup.json
media-manager workflow profile-run .\profiles\family-cleanup.json --show-command
```

### Inventory and audit

```powershell
media-manager workflow profile-list --profiles-dir .\profiles
media-manager workflow profile-audit --profiles-dir .\profiles
media-manager workflow profile-run-dir --profiles-dir .\profiles --only-valid
```

### Useful profile filters

```powershell
media-manager workflow profile-list --profiles-dir .\profiles --workflow cleanup
media-manager workflow profile-list --profiles-dir .\profiles --preset cleanup-family-library
media-manager workflow profile-list --profiles-dir .\profiles --profile-name-contains family
media-manager workflow profile-audit --profiles-dir .\profiles --profile-path-contains family\
```

## Bundles

### Write and inspect

```powershell
media-manager workflow profile-bundle-write .\bundles\profiles.json --profiles-dir .\profiles
media-manager workflow profile-bundle-show .\bundles\profiles.json
media-manager workflow profile-bundle-audit .\bundles\profiles.json
```

### Compare and merge

```powershell
media-manager workflow profile-bundle-merge .\bundles\merged.json .\bundles\a.json .\bundles\b.json --prefer last
media-manager workflow profile-bundle-compare .\bundles\before.json .\bundles\after.json --only-changed
```

### Extract, sync, run

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

## History and review

### Broad history

```powershell
media-manager workflow history --path .\runs
media-manager workflow history --path .\runs --summary-only
media-manager workflow history --path .\runs --json
```

### Narrowed history

```powershell
media-manager workflow history --path .\runs --command organize --only-failed
media-manager workflow history --path .\runs --record-type execution_journal --has-reversible-entries
media-manager workflow history --path .\runs --created-at-after 2026-04-01T00:00:00Z --created-at-before 2026-04-30T23:59:59Z
```

### Latest matching event

```powershell
media-manager workflow last --path .\runs
media-manager workflow last --path .\runs --command trip --only-successful --only-apply
```

### Latest matching event per command

```powershell
media-manager workflow history-latest-by-command --path .\runs
media-manager workflow history-latest-by-command --path .\runs --only-failed
media-manager workflow history-latest-by-command --path .\runs --summary-only
```

## Safe operational loop

A practical low-risk workflow is:

1. render or save a preset
2. inspect or validate the profile
3. preview or audit the bundle/profile selection
4. run the workflow
5. inspect workflow history
6. inspect the latest matching event or latest-per-command view

That loop keeps the CLI workflow layer useful as an operational product instead of a thin convenience wrapper.
