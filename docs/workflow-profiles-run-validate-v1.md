# Workflow profiles run and validate v1

This package extends the preset/profile layer with two practical commands:

- `media-manager workflow profile-validate <PROFILE.json>`
- `media-manager workflow profile-run <PROFILE.json>`

## What profile-validate does

It loads a workflow profile, checks that:

- the referenced preset exists
- the preset points to a known workflow
- all required values are present
- the resulting command preview can be rendered

It then reports whether the profile is valid and shows the rendered command preview.

## What profile-run does

It loads a validated profile and delegates directly to the underlying workflow command.

Examples:

```bash
media-manager workflow profile-validate profiles/family-cleanup.json
media-manager workflow profile-run profiles/family-cleanup.json
media-manager workflow profile-run profiles/italy-trip.json --show-command
```

## Notes

- This is still a CLI-first feature.
- Command previews are shown as shell-friendly text, but delegated execution uses argument lists directly.
- Invalid profiles fail before any delegated workflow command is started.
