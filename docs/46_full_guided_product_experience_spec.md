# Full Guided Product Experience Spec

## Purpose

This document captures the intended end-state user experience for the guided Media Manager product.

It is not a small UI tweak note.
It is the product-level target for the modern guided workflow and should be treated as the north-star reference for future implementation decisions.

## Core Product Direction

Media Manager is intended to become a modern local desktop application for photo and video cleanup, duplicate handling, sorting, renaming, and optional trip/session grouping.

The preferred user path is the guided workflow.
Manual tools remain available, but the product should clearly promote the workflow as the default and more capable path.

The visual direction is:
- modern desktop app
- calm, premium, centered layouts
- large typography in primary views
- no old tile-dashboard feel
- strong emphasis on one main decision per step
- information density that grows only when the window grows

## Home Page Experience

### Layout
The home page should keep:
- side navigation on the left
- a large, bold, centered title at the top of the main area
- a short centered subtitle or explanation below
- the guided questionnaire vertically stacked and centered
- large buttons that immediately start the workflow
- a dismiss action below the questionnaire
- a polished explanation section below the dismiss action explaining the idea of the product and how it works

### Questionnaire options
The home questionnaire should present a short set of problem-first choices, not technical tool choices.

The choices should be vertically stacked, centered, large, and immediately actionable.

### Dismiss behavior
If the user dismisses the questionnaire, the questionnaire should disappear and the product explanation should remain visible.

## Workflow Shell Experience

Once the user starts the workflow, the workflow page becomes the main place where the guided process happens.

### General shell rules
- Each step is presented as a large central stage.
- The base application window should remain relatively compact by default.
- Content should scale up when the user enlarges the window, but the base design should not assume a huge window.
- The left bottom area should keep a back button.
- The bottom information strip should stay visible across workflow stages.

## Persistent Bottom Strip

The bottom strip should always show:
- source folder count
- live count of detected or processed files
- selected action mode
- current step and remaining step count
- a central rotating tip/fact area similar in spirit to a game loading screen

### Rotating content rules
The rotating strip should include:
- practical workflow tips
- photography facts
- photography history / background facts
- benefits of careful cleanup
- positive information about why the workflow helps

The tone should feel informative and pleasant, not childish or noisy.

## Guided Workflow Order

For the full guided path, the intended order is:
1. Source folders
2. Target folder
3. Operation mode
4. Exact duplicate review
5. Rich duplicate / similarity comparison stage
6. Cleanup summary
7. Dry run / adjustment / execution
8. Sorting builder
9. Sorting execution
10. Rename builder
11. Rename execution
12. Optional trip/session grouping stage if enabled
13. Final congratulations screen

The visible step indicator should update when optional stages are enabled.

## Step 1: Source folders

The user first selects source folders.

Rules:
- the step should feel minimal and clear
- only the relevant controls should be visible
- a short confirmation should be shown after a folder is selected
- background scanning may already begin here where useful

## Step 2: Target folder

The user selects the target folder.

Rules:
- show a short confirmation after selection
- explain that the action mode can still be adjusted later
- keep the page centered and clean
- continue the live scan and statistics in the bottom strip

## Step 3: Operation mode

The user chooses what should happen to files later:
- copy
- move
- delete

This should be a centered, simple decision step.
A note should clarify that the choice can still be changed later.

## Step 4: Exact duplicate review stage

This stage should visually begin with a start button, but the system may already have done meaningful scanning work in the background.

### Start button behavior
The start button is intentionally part UX theater and part control surface.
It starts the visible review experience, even if background work was already underway.

### Progress handling
A progress bar should clearly communicate that the system is still working.
The bar should be visually integrated into the GUI and animated.

### Table behavior
After the visible review begins, a modern table appears.
Rows should appear with a small, unobtrusive delay so it feels like the system is actively producing results.

Each row should include at least:
- file name with extension
- file size
- date
- number of duplicates
- match percentage
- actions such as show / inspect

### Quick duplicate popup
When the user opens a duplicate item, a foreground popup should appear.
This popup is a temporary review surface and should explicitly tell the user that it is not the final comparison tool.

The popup should:
- adapt to item count and window size
- show all found exact duplicates
- allow selection of one item
- provide useful actions such as keep, delete, keep one / delete others, and close / back
- continue allowing the system to keep working in the background

## Step 5: Rich duplicate and similarity comparison stage

After exact duplicates are reviewed, the user should enter a richer comparison stage.

### Overall layout
- left side: source-side comparison table with richer metadata
- right side: target-side or chosen-survivor table, visibly narrower
- above the tables: two preview areas for images or videos

### Preview rules
- the left preview shows the currently selected source candidate
- the right preview shows the selected target or survivor candidate
- when there are multiple candidates on a side, small previews may be shown
- clicking a preview should enlarge it
- enlarged preview should have a clear close control, for example an X that visibly reacts on hover

### Similarity handling
The table should be sorted from strongest similarity downward.
The lower bound should be around 50 percent.
There should be a clear visual separator or warning around 70 percent because below that confidence becomes weaker.

Users should be able to skip lower-confidence comparison ranges if they choose.

## Related files and associated media handling

This product should not pretend that every media file is standalone.
Real libraries often contain related files such as:
- RAW + JPEG pairs
- drone sidecar data
- manufacturer-specific auxiliary files
- video-related companion files

Rules:
- related files should still be treated as real files
- the app should try to detect relationships where possible
- the app should tell the user that this is best-effort behavior, not perfect certainty
- if the system is confident enough, associated files may be moved together with the chosen survivor
- if the system is not confident, those files may be placed into a clearly structured safe holding folder in the source area instead of being destroyed recklessly
- unsupported display formats should still show an error/fallback in preview without weakening confidence in true 100 percent duplicate detection
- when preview is not possible, the app should offer opening the file externally with the system default program

## Cleanup summary stage

After duplicate decisions are finished, the product should show a large, centered summary stage.

It should include:
- number of scanned files
- number of duplicates
- number of unknown files
- number of associated files detected
- what happened to associated files
- selected action mode with ability to adjust it again
- a large, visually satisfying indication of saved space or expected saved space

## Dry run and execution adjustment stage

Before real execution, the product should offer a dry run.

The dry-run surface should:
- list all planned copy / move / delete operations
- allow filtering by action type
- show a reason for destructive actions, such as exact duplicate, user decision, percentage-based match decision, and so on
- allow selecting a row to inspect or change the action
- allow previewing or opening the involved file where possible

After the dry run, the user may execute the real operation.
A progress animation and progress bar should accompany the real work.

## Sorting stage

After cleanup execution, the product should move into sorting.

### Sorting configuration goals
The user should be able to define the target folder structure visually.

The default proposal is three levels:
- year
- month
- day

The user should be able to:
- add levels on either side
- remove levels
- choose between meaningful style variations for each level

Examples:
- year in different formats
- month as number, full name, or combined forms
- day as useful date-oriented variants

The currently built path template should be displayed prominently above the change controls and should update live.

### Optional trip/session path
The sorting stage should ask whether the user wants later help with vacations, trips, sessions, or similar groupings.
If enabled, the workflow gains an extra later step and the step indicator updates accordingly.

## Rename stage

The rename stage should allow file naming from reusable blocks.

Capabilities should include:
- adding naming blocks at beginning or end
- including original name at start or end
- readable date/time blocks
- a dropdown with predefined templates
- templates that automatically create, remove, or fill the relevant naming blocks

This stage should remain centered, large, and visually consistent with the rest of the workflow.

## Optional trip / session grouping tool

If enabled, the user should later reach a trip/session grouping tool.

Capabilities:
- select date range
- refine with time range
- view all affected images and videos as small but readable previews
- sort by earliest or latest
- exclude individual or multiple files
- choose whether files are moved, copied, or linked into the trip
- default is move
- stored trip/session definitions remain editable later
- if trip creation empties folders, those folders may be removed

This tool should remain flexible enough to support vacations, day trips, photo sessions, and other user-defined groupings.

## Final congratulations screen

The final screen should summarize what was achieved and close the guided process cleanly.
Later, a donation option such as "buy me a coffee" may be added, but it should stay secondary.

## Manual tools strategy

Manual tools remain available, but they should increasingly reuse workflow logic.

When a manual tool is started outside an already-known optimized target, the user should be encouraged toward the workflow first.
If the target is recognized as already processed, the software should reuse stored data and avoid repeating unnecessary warnings.

## Resume and hidden workflow state

The system should store hidden workflow data in the target system so that:
- crashes are recoverable
- accidental closes are recoverable
- existing optimized targets can be reopened and continued
- the stored state can be compared against current reality before it is trusted

This hidden state should support long-running workflows and later revisits.
