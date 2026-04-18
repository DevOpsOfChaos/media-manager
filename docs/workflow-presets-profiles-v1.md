# Workflow presets / profiles v1

This block adds a first reusable presets layer on top of the workflow shell.

## Why this exists

Many realistic media-manager runs repeat the same setup patterns:

- cleanup across several source folders into one library target
- trip collection with a known date range
- duplicate review with a conservative keep policy
- date-based organization
- standardized rename templates

Typing every flag again and again is noisy and error-prone.

## What v1 adds

### Built-in presets

The workflow shell now knows a small set of built-in presets:

- `cleanup-family-library`
- `trip-hardlink-collection`
- `duplicate-review-safe`
- `organize-date-library`
- `rename-capture-standard`

### Profile files

A profile file stores:

- `schema_version`
- `profile_name`
- `preset`
- `values`

Example:

```json
{
  "schema_version": 1,
  "profile_name": "Italy 2025",
  "preset": "trip-hardlink-collection",
  "values": {
    "source": ["C:/Phone", "D:/Camera"],
    "target": "E:/Trips",
    "label": "Italy_2025",
    "start": "2025-08-01",
    "end": "2025-08-14"
  }
}
```

## New commands

List presets:

```bash
media-manager workflow presets
```

Show one preset:

```bash
media-manager workflow preset-show cleanup-family-library
```

Render a command preview from a preset:

```bash
media-manager workflow render-preset cleanup-family-library --source C:/Photos --source D:/Phone --target E:/Library
```

Load a profile file and render its command preview:

```bash
media-manager workflow profile-show C:/profiles/italy-trip.json
```

## Scope of v1

This is still a preview-and-reuse layer.

It does not yet:

- save profiles from the CLI
- validate every workflow flag in depth
- provide per-user preset storage
- provide GUI editing for profiles

Those can build on this foundation later.
