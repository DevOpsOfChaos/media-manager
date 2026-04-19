# Workflow Command Matrix

This document is a compact orientation map for the current workflow-oriented command surface.

It is not meant to repeat every help screen. It is meant to answer:

- which command family should I look at?
- what does it operate on?
- what kind of output or side effect should I expect?

## Discovery and guidance

| Command | Main purpose | Input focus | Typical result |
|---|---|---|---|
| `workflow list` | list available workflows | none | overview |
| `workflow show` | describe one workflow | workflow name | explanation |
| `workflow problems` | list common user problems | none | guided choices |
| `workflow recommend` | recommend one workflow | problem slug | suggested path |
| `workflow wizard` | guided workflow selection | flags/answers | recommendation + commands |
| `workflow presets` | list built-in presets | none | preset inventory |
| `workflow preset-show` | inspect one preset | preset name | preset details |
| `workflow render-preset` | render one preset command | preset + overrides | command preview |

## Saved profile commands

| Command | Main purpose | Input focus | Typical result |
|---|---|---|---|
| `workflow profile-save` | create/update a saved profile | preset + values | JSON profile file |
| `workflow profile-show` | inspect one saved profile | profile path | command preview |
| `workflow profile-validate` | validate one saved profile | profile path | validation result |
| `workflow profile-run` | delegate one saved profile | profile path | delegated CLI run |
| `workflow profile-list` | inventory profile files | profiles directory | list + summary |
| `workflow profile-audit` | audit profile files | profiles directory | invalid/valid summary |
| `workflow profile-run-dir` | batch-run selected profiles | profiles directory | batch execution summary |

Useful profile filters:

- `--workflow`
- `--preset`
- `--profile-name-contains`
- `--profile-path-contains`
- `--only-valid`
- `--only-invalid`

## Bundle commands

| Command | Main purpose | Input focus | Typical result |
|---|---|---|---|
| `workflow profile-bundle-write` | export selected profiles into a bundle | profiles directory | bundle JSON |
| `workflow profile-bundle-show` | inspect one bundle | bundle path | list + summary |
| `workflow profile-bundle-audit` | validate one bundle | bundle path | invalid/valid summary |
| `workflow profile-bundle-extract` | restore profiles from a bundle | bundle + target dir | written/skipped/conflicts |
| `workflow profile-bundle-sync` | preview/apply a bundle against a directory | bundle + target dir | sync plan/result |
| `workflow profile-bundle-merge` | combine multiple bundles | bundle paths | merged bundle |
| `workflow profile-bundle-compare` | compare two bundles | two bundle paths | comparison summary |
| `workflow profile-bundle-run` | batch-run selected bundle profiles | bundle path | execution summary |
| `workflow profile-bundle-list-dir` | inventory many bundle files | bundles directory | list + summary |
| `workflow profile-bundle-audit-dir` | audit many bundle files | bundles directory | problematic/clean summary |
| `workflow profile-bundle-run-dir` | batch-run profiles across bundle files | bundles directory | execution summary |

Useful bundle filters:

- `--workflow`
- `--preset`
- `--profile-name-contains`
- `--relative-path-contains`
- `--only-valid`
- `--only-invalid`
- `--only-clean-bundles`
- `--only-problematic-bundles`

## History and audit commands

| Command | Main purpose | Input focus | Typical result |
|---|---|---|---|
| `workflow history` | list matching history entries | history directory | entries + summary |
| `workflow last` | show one newest matching entry | history directory | one entry |
| `workflow history-latest-by-command` | show newest matching entry per command | history directory | reduced grouped list |

Useful history filters:

- `--command`
- `--record-type`
- `--only-successful`
- `--only-failed`
- `--only-apply`
- `--only-preview`
- `--has-reversible-entries`
- `--min-entry-count`
- `--min-reversible-entry-count`
- `--created-at-after`
- `--created-at-before`

## Delegated workflow commands

| Command | Main purpose | Input focus | Typical result |
|---|---|---|---|
| `workflow run cleanup ...` | direct delegated run | raw workflow args | delegated CLI behavior |
| `workflow run organize ...` | direct delegated run | raw workflow args | delegated CLI behavior |
| `workflow run rename ...` | direct delegated run | raw workflow args | delegated CLI behavior |
| `workflow run duplicates ...` | direct delegated run | raw workflow args | delegated CLI behavior |
| `workflow run trip ...` | direct delegated run | raw workflow args | delegated CLI behavior |

## How to choose quickly

Use this rough rule of thumb:

- Need help choosing? Start with discovery/wizard commands.
- Need repeatability? Save a profile.
- Need batch reuse or handoff? Write a bundle.
- Need review and triage? Use history commands.
- Need raw control? Use delegated workflow runs.

## Compatibility note

When expanding the workflow command surface:

- prefer additive new commands over reshaping existing JSON contracts
- keep filter naming consistent across history commands
- do not silently change output fields that may already be used in tests or automation
