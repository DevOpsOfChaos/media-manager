# Workflow presets / profiles v2

This package combines:

1. a fix for preset rendering with list-valued fields such as `source`
2. the next workflow step: saving reusable workflow profiles directly from the CLI

## Fixed bug

`render_workflow_preset_command(...)` no longer crashes when required values contain lists.
The missing-value check now handles:

- `None`
- empty strings
- empty lists

## New command

```bash
media-manager workflow profile-save <PATH.json> --preset <PRESET> [values...]
```

Example:

```bash
media-manager workflow profile-save profiles/family-cleanup.json   --preset cleanup-family-library   --profile-name "Family cleanup"   --source C:/Photos   --source D:/Phone   --target E:/Library
```

## Current profile-save behavior

- validates the preset name
- validates required values by rendering the effective command
- writes normalized JSON with `schema_version = 1`
- refuses to overwrite existing files unless `--overwrite` is passed
