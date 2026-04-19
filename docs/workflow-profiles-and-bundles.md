# Workflow profiles and bundles

This document explains how the current workflow productivity layer is meant to be used.

## Why profiles exist

A profile lets you save a workflow configuration that you expect to run again.

Typical reasons:

- the same source folders are reused often
- the same organize or rename conventions are reused often
- a cleanup or trip collection is performed repeatedly
- the team wants reviewable JSON files instead of copy-pasting long commands

## Why bundles exist

A bundle is a higher-level container for multiple saved profiles.

Typical reasons:

- snapshot a profile collection before changes
- compare two profile collections later
- merge several collections together
- move valid profiles to another directory
- batch-run a selected set of valid profiles

## Recommended flow

### 1. Start with a preset

```powershell
media-manager workflow presets
media-manager workflow preset-show cleanup-family-library
```

### 2. Render and inspect the command

```powershell
media-manager workflow render-preset cleanup-family-library --source C:\Photos --source D:\Phone --target E:\Library
```

### 3. Save a profile

```powershell
media-manager workflow profile-save .\profiles\family-cleanup.json --preset cleanup-family-library --source C:\Photos --source D:\Phone --target E:\Library
```

### 4. Validate and inventory profiles

```powershell
media-manager workflow profile-validate .\profiles\family-cleanup.json
media-manager workflow profile-list --profiles-dir .\profiles
media-manager workflow profile-audit --profiles-dir .\profiles
```

### 5. Write a bundle snapshot

```powershell
media-manager workflow profile-bundle-write .\bundles\profiles.json --profiles-dir .\profiles
```

### 6. Compare or sync later

```powershell
media-manager workflow profile-bundle-compare .\bundles\before.json .\bundles\after.json
media-manager workflow profile-bundle-sync .\bundles\profiles.json --target-dir .\profiles-restored --apply
```

## Selection filters for large collections

Once profile collections get larger, workflow/preset filters alone are often not enough.

The workflow CLI now supports two additional narrowing layers:

### Profile directory filters

- `--profile-name-contains <TEXT>`
- `--profile-path-contains <TEXT>`

Examples:

```powershell
media-manager workflow profile-list --profiles-dir .\profiles --profile-name-contains family
media-manager workflow profile-audit --profiles-dir .\profiles --profile-path-contains trips\
media-manager workflow profile-run-dir --profiles-dir .\profiles --profile-name-contains cleanup --only-valid
```

### Bundle filters

- `--profile-name-contains <TEXT>`
- `--relative-path-contains <TEXT>`

Examples:

```powershell
media-manager workflow profile-bundle-show .\bundles\profiles.json --relative-path-contains family\
media-manager workflow profile-bundle-run .\bundles\profiles.json --profile-name-contains trip --only-valid
media-manager workflow profile-bundle-list-dir --bundles-dir .\bundles --profile-name-contains family
```

### Important path note

Path-based filters are normalized so slash and backslash variants are treated the same.

That matters on Windows because:

- stored relative bundle paths should remain portable slash-style paths
- local filesystem paths may still be represented with backslashes
- users should not need to remember which separator form a command expects

## Safety expectations

The current direction is review-first, not blind mass execution.

That means:

- validate profiles before depending on them
- audit profile directories and bundles before large batch runs
- use `--only-valid` when you want a stricter selection
- use `--show-command` whenever you want human-readable confirmation
- use `--json` when another script or tool should consume the result

## Windows-specific note

JSON bundle paths should be stable and portable even on Windows.

That is why relative paths inside bundle-style artifacts should be treated as slash-separated logical paths rather than platform-specific display paths.

## Current limitations

The profile/bundle layer is already useful, but it is still part of an actively hardened CLI/core product line.

So the right expectation is:

- serious and increasingly practical
- not yet final
- worth documenting clearly so future maintenance stays easier
