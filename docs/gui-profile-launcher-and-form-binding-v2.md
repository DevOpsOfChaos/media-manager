# GUI profile launcher and form binding v2

This block expands the new shell scaffold with two connected capabilities:

- launcher models for built-in presets and saved profiles
- bound workflow forms that carry current values, missing required fields, and command previews

## New shell commands

- `media-manager shell --dump-launchers`
- `media-manager shell --dump-launchers --profiles-dir <DIR>`
- `media-manager shell --preview-preset-form <PRESET>`
- `media-manager shell --preview-profile-form <PROFILE.json>`
- `media-manager shell --preview-profile-command <PROFILE.json>`

## What launcher data includes

Each launcher item describes:

- whether it comes from a preset or a saved profile
- workflow name
- preset/profile identity
- validity
- missing required fields
- command preview when renderable
- human-readable problems

## What bound form data includes

A bound form model now carries:

- workflow metadata
- the bound preset/profile name
- field values
- field value source
- missing required fields
- validity
- problems
- optional command preview

## Notes

This is still a shell/backend-oriented step. It does not try to build a full data-entry GUI yet.
Instead, it provides the structured models that a later GUI form layer can consume with less risk.
