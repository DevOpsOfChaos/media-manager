# Similar Duplicates Review v2

This step extends the earlier similar-image scan with a safer review layer.

## Goal

Surface likely visual duplicates as **review candidates** without pretending the tool
can safely delete them automatically.

## New CLI options

```powershell
media-manager duplicates --source C:\Photos --similar-images --show-similar-review
```

Optional policy:

```powershell
media-manager duplicates --source C:\Photos --similar-images --similar-policy newest --show-similar-review
```

## Output idea

For each similar-image group, the tool now recommends one keep candidate and marks
the remaining files as review candidates.

Status values:

- `keep`
- `review-candidate`

## Keep policy

The review layer supports:

- `first`
- `newest`
- `oldest`

This is only a **recommendation policy**. It does not delete or move similar-image
candidates automatically.

## JSON report

When `--json-report` is used together with `--similar-images`, the report now contains
a `similar_review` block with:

- keep policy
- group count
- row count
- keep count
- review candidate count
- one row per reviewed file

## Safety note

This remains a review-only feature.

Visually similar images are not the same as exact duplicates. Crops, edits, screenshots,
and burst-series shots often need human review before any destructive action.
