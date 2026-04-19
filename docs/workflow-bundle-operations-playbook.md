# Workflow Bundle Operations Playbook

This playbook is for repeated real-world use of workflow profile bundles.

The bundle layer is no longer just archival scaffolding. It is now one of the main productivity surfaces for moving, auditing, comparing, syncing, and batch-running repeatable workflow configurations.

## Bundle lifecycle at a glance

A common lifecycle looks like this:

1. create or refine profiles
2. audit the profile directory
3. export selected profiles into a bundle
4. inspect or compare the bundle
5. extract or sync the bundle into another location
6. run valid bundle profiles in batch

## Safe default sequence

### 1. Audit the source profiles first

```powershell
media-manager workflow profile-audit --profiles-dir .\profiles
```

Reason:

- invalid profiles are easier to fix before they are packed into a bundle
- this keeps later bundle operations simpler and cleaner

### 2. Write a focused bundle, not a kitchen-sink bundle

```powershell
media-manager workflow profile-bundle-write .\bundles\family.json --profiles-dir .\profiles --profile-name-contains family
```

Reason:

- smaller thematic bundles are easier to review and compare
- they reduce confusion during sync and batch-run operations

### 3. Inspect the bundle immediately

```powershell
media-manager workflow profile-bundle-show .\bundles\family.json
```

Reason:

- confirms what really got selected
- catches path and filter mistakes early

### 4. Audit before running or syncing

```powershell
media-manager workflow profile-bundle-audit .\bundles\family.json
```

Reason:

- invalid bundle profiles should be visible before operational use
- this is especially important after merge operations

## Compare and merge patterns

### Compare before replacing an existing bundle

```powershell
media-manager workflow profile-bundle-compare .\bundles\before.json .\bundles\after.json --only-changed
```

Use this when:

- you changed presets or values
- you refreshed a bundle from a profile directory
- you want to review drift before rollout

### Merge with an explicit conflict rule

```powershell
media-manager workflow profile-bundle-merge .\bundles\merged.json .\bundles\team-a.json .\bundles\team-b.json --prefer last
```

Guideline:

- use `--prefer last` when later inputs should override earlier ones
- use `--prefer first` when earlier inputs are the authority

Do not merge casually without knowing which side is supposed to win.

## Extract vs. sync

### Extract

```powershell
media-manager workflow profile-bundle-extract .\bundles\profiles.json --target-dir .\profiles-restored
```

Choose extract when:

- you want to restore or materialize bundle contents
- you do not want pruning logic
- you want a straightforward write-out of selected profiles

### Sync

```powershell
media-manager workflow profile-bundle-sync .\bundles\profiles.json --target-dir .\profiles-restored
```

Choose sync when:

- you care about previewing differences first
- you want a managed target directory
- you may later use `--apply`, `--overwrite`, or `--prune`

Safe habit:

1. run sync in preview mode
2. inspect the summary and entries
3. only then add `--apply`

## Batch-run guidance

```powershell
media-manager workflow profile-bundle-run .\bundles\profiles.json --only-valid
```

Recommended defaults:

- prefer `--only-valid`
- use thematic bundles instead of giant mixed bundles
- only add `--continue-on-error` when partial execution is actually desired

## Directory-level bundle operations

For larger collections:

```powershell
media-manager workflow profile-bundle-list-dir --bundles-dir .\bundles
media-manager workflow profile-bundle-audit-dir --bundles-dir .\bundles
media-manager workflow profile-bundle-run-dir --bundles-dir .\bundles --only-clean-bundles
```

This is useful when a repository or team keeps multiple bundle files with different roles.

## Windows-specific reminders

- prefer path checks that tolerate slash and backslash variants
- keep portable bundle-relative paths stable
- when testing path-sensitive behavior, include Windows-style cases explicitly

## Maintainer checklist before shipping bundle changes

1. profile inventory tests
2. bundle write/show/audit tests
3. compare/merge tests
4. extract/sync tests
5. directory-level bundle tests
6. full `pytest -q`

Bundle changes often look local while actually depending on:

- profile validation
- path normalization
- `__init__` exports
- JSON compatibility

That is why broad regression is mandatory here.
