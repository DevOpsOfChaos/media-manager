# Duplicate Comparison and Associated Files Spec

## Purpose

This document narrows the full product vision down to the duplicate-comparison, preview, and associated-file handling layers.

This area is one of the most important trust surfaces in the product and should not be reduced to a simple duplicate table.

## Phase split

The product should conceptually separate duplicate handling into at least two phases:

1. Exact duplicate review
2. Similarity-based and target-aware comparison

The current quick duplicate popup is only a temporary review surface and should remain explicitly framed that way.

## Exact duplicate review phase

### Goal
Handle byte-identical files safely and quickly.

### Table behavior
The exact-duplicate table should:
- populate gradually after the visible start action
- communicate active work through row reveal and progress animation
- remain visually calm and readable

### Row content
Each row should show at least:
- full file name with extension
- size
- relevant timestamp
- duplicate count
- confidence / match information
- actions to inspect the group

### Quick review popup
The popup shown from the exact-duplicate table is a temporary intermediate tool.
A clear note should explain that this is not the final comparison environment.

The popup should support:
- selecting a candidate
- keeping one candidate
- deleting one or more candidates
- keeping one and deleting the rest
- closing / going back

## Rich comparison phase

After exact duplicates, the user should move into a more advanced comparison stage.

### Layout expectations
The comparison stage should use:
- a wide source-side table with rich metadata
- a narrower target-side table
- preview areas above the tables
- stronger focus on comparison confidence and decision quality

### Sorting by confidence
The items should be sorted from highest confidence downward.
The user should understand that very high confidence results are safer than weak similarity matches.

A practical lower bound of around 50 percent is acceptable.
A visible threshold or separator should appear around 70 percent to communicate decreasing confidence.

### Preview expectations
The preview system should handle both images and videos.
If multiple candidate files exist, small previews should be shown where useful.
Clicking a preview should enlarge it.
The enlarged preview should have a clear close control.

## Associated file handling

A real media cleanup tool must handle related files intelligently enough to avoid breaking media workflows.

Examples include:
- RAW + JPEG pairs
- drone sidecars
- manufacturer metadata files
- video companion files

### Product principles
- related files are still real files and must not be ignored
- detection should be best-effort, not fake certainty
- the UI should tell the user that the software tries to help but may not be perfectly sure
- when confidence is high enough, associated files may follow the chosen survivor
- when confidence is not high enough, the system should prefer safe containment over silent destruction

### Safe containment behavior
If the system is uncertain, associated files may be placed into a structured holding area in the source side, for example grouped into folders based on the related media file.

This preserves data and keeps manual cleanup possible.

## Preview fallback rules

The software should try to support as many image and video formats as practical.
However, unsupported preview formats must not break trust.

If preview cannot be generated:
- show a clear preview limitation message
- explain that exact 100 percent duplicate confidence still remains valid where applicable
- offer opening the file externally with the system default program

## User control and automation balance

The product should automate obvious safe wins, but it should not hide uncertainty.

### Example
For clear 100 percent exact duplicates, the user may be offered a bulk action such as merging all 100 percent exact duplicates automatically.

But the associated-file handling note should remain visible:
- the software tries to include related files intelligently
- users should still verify high-value edge cases themselves

## Transition into summary

Once the duplicate/comparison phase is complete, the resulting decisions should feed into the summary, dry-run, and execution layers in a transparent way.

No hidden destructive action should happen before the user sees the resulting plan.
