# GUI profile launcher and form binding v2

This update connects the shell more directly to presets and saved profiles.

New headless shell capabilities:

- `media-manager shell --dump-launchers --profiles-dir <DIR>`
- `media-manager shell --preview-preset-form <PRESET>`
- `media-manager shell --preview-profile-form <PROFILE.json>`
- `media-manager shell --preview-profile-command <PROFILE.json>`

The shell can now inspect:

- built-in presets as launcher cards
- saved workflow profiles discovered in a directory
- form models that are prefilled from preset defaults
- form models that are prefilled from saved profile values

This is still a scaffold layer, but it is much closer to a future modern GUI because the UI can now work from:

- workflow metadata
- form metadata
- preset defaults
- saved profile values
