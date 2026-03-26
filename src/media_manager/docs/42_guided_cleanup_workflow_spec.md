# Guided Cleanup Workflow Spec

## Workflow Overview

The full guided workflow should proceed through these stages:

1. Select source folders
2. Select target folder
3. Choose action mode
4. Exact duplicate review
5. Similarity-assisted review
6. Cleanup summary and dry run
7. Execute cleanup
8. Sorting configuration
9. Execute sorting
10. Rename configuration
11. Execute renaming
12. Optional trip/session workflow
13. Congratulations / completion

The visible step bar should update when optional stages are enabled or skipped.

## Shared Workflow UI Pattern

Every workflow page should follow one visual pattern:

- centered main content
- one main decision domain per page
- left bottom back button
- large primary action button only when the current stage is actually ready
- bottom persistent info strip shown on every workflow page

### Persistent bottom strip
The bottom strip should always show:
- source folder count
- live scanned file count
- selected mode
- current step / remaining steps
- center area for rotating facts, tips, benefits, and photography history snippets

Rules for the center tip strip:
- placed centrally
- short text only
- more readable colors than gray-on-dark-blue
- updates every 15 seconds, not too fast
- copy can include photography facts, media management benefits, and positive “loading screen” style text

## Stage 1: Source folders

The user selects one or more source folders.

UX rules:
- no clutter
- clean folder count summary
- scanning can already begin in background
- user should get a small confirmation after successful selection
- live file count starts increasing here

## Stage 2: Target folder

The user selects a target folder.

UX rules:
- confirmation after selection
- note that later workflow state may be stored hidden inside the target system
- still allow easy back navigation

## Stage 3: Action mode

Ask what should happen to files:
- copy
- move
- delete

Rules:
- centered presentation
- strong readability
- user should be told the choice can be adjusted later before final execution

## Stage 4: Exact duplicate review

The scan is already running before the visible start button is pressed.

### Start button behavior
The visible start button is mostly performative UX. It starts the visible review state, while the backend may have already prepared real results.

### Progress
A visually integrated progress bar should communicate current progress.

### Duplicate table
Rows appear with slight, subtle delay so it feels alive.
Each row should include:
- file name with extension
- size
- date
- duplicate count
- match score
- action button

### Duplicate detail popup
The popup is a temporary review layer, not the final comparison tool.
A small note should make this clear.

Popup capabilities:
- show all duplicate candidates
- select one or more items
- keep one
- delete selected
- keep one and remove others
- close / go back

The popup must adapt to candidate count and window size.

## Stage 5: Similarity-assisted review

This stage starts after exact matches.

The UI now becomes comparison-focused:
- left table: source-side candidates / unresolved items
- right table: selected target / surviving result side
- image or video preview areas above
- support enlarged preview
- if unsupported preview, show fallback message and allow external-open action

### Similarity thresholds
The system should support review down to 50 percent.
Around 70 percent there should be a clear visual trust break, warning that results are less reliable.

### Related files
The system should try to detect and handle associated files:
- manufacturer sidecars
- RAW + JPEG pairs
- drone/camera extras

Rules:
- related files should not silently decide core duplicate status
- the app should try to keep associated files with the selected survivor when sensible
- if uncertain, keep them organized in a safe holding structure instead of deleting recklessly
- the user should be told that the software tries to help but does not guarantee perfect association behavior

## Stage 6: Cleanup summary and dry run

After duplicate and similarity handling, show a summary page with:
- total scanned files
- duplicates found
- unknown files
- related files detected
- what happened to related files
- current action mode
- estimated storage saved

This page should be large, centered, and celebratory but still practical.

### Dry run
Before execution, offer a dry run.

Dry run viewer should:
- list copy / move / delete actions
- allow sorting/filtering by action type
- show reason for each delete or move
- allow row selection
- allow item inspection or action adjustment

## Stage 7: Cleanup execution

Show:
- animated progress
- running state
- confidence-building feedback
- updated totals in the bottom strip

## Completion criteria for cleanup
Cleanup is complete only when all planned decisions are reflected in the execution plan and the user has explicitly confirmed execution or dry-run inspection.
