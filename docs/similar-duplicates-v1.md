# Similar Duplicates Foundation v1

This block adds a first safe foundation for **likely similar images**.

## Scope

- image files only
- perceptual review only
- no automatic delete or keep decisions
- integrated into `media-manager duplicates`

## Why this is a foundation only

Similar-image detection is inherently probabilistic.
Unlike exact duplicates, it should not jump directly into destructive actions.

This first version therefore focuses on:

- scanning supported image files
- computing a simple perceptual hash
- grouping visually related candidates
- exposing the result in CLI output and JSON reports

## Current CLI options

- `--similar-images`
- `--show-similar-groups`
- `--similar-threshold <N>`

## Supported image formats in v1

- `.jpg`
- `.jpeg`
- `.png`
- `.bmp`
- `.gif`
- `.tif`
- `.tiff`
- `.webp`

## Important limitation

This version does **not** yet integrate similar-image decisions into cleanup execution.
It is a review-oriented analysis layer.

## Dependency note

This feature uses Pillow.
After applying the ZIP, refresh local dependencies if needed:

```powershell
python -m pip install -e ".[dev]"
```
