# Workflow UX Target

This document captures the intended end-state user flow for the main guided workflow.

It is a target specification, not a claim that every step is already implemented.

---

## 1. Home page

### Layout target

The home page should contain:

- a very large centered product title at the top,
- a large guided questionnaire block occupying most of the page,
- four large stacked problem buttons centered vertically and horizontally,
- a centered dismiss action below the questionnaire,
- a larger "How it works" section below,
- no direct tool tiles on the home page,
- manual tools only in the side navigation.

### Questionnaire entry copy

Example intent:

- "Choose your problem to start a guided workflow."

### Problem options

The user picks one of the following broad situations:

1. full cleanup,
2. duplicates already handled, now organize,
3. already organized, only rename,
4. exact duplicate review only.

The visual priority must be large, simple, and low-text.

### Dismiss behavior

If the user dismisses the questionnaire:

- the questionnaire disappears,
- the page keeps the product explanation section,
- the user can restart the questionnaire from a single clear action below.

### Language switch

The top-right corner should later show a proper language toggle using US and German flag assets.

English remains the default language.

---

## 2. Workflow shell

After a problem is chosen, the user is taken into the workflow area.

From there on, the main interaction should happen inside large step pages rather than many small utility panels.

### Global workflow shell requirements

Every workflow step should later share:

- large centered step content,
- an always-visible back action at the lower left,
- a bottom information bar,
- progress indication,
- subtle animation and transition feedback,
- a layout that stays compact at base window size and grows gracefully when the window grows.

### Bottom information bar target

The bottom bar should show:

- selected source directory count,
- selected target directory,
- current file operation mode,
- current workflow step,
- number of remaining steps,
- a live file count discovered during scanning,
- a rotating stream of tips, photography facts, product benefits, and small fun facts.

This is intentionally inspired by the feel of a game loading/status bar, but should remain clean and premium.

---

## 3. Step order for the full workflow

For the full workflow, the intended order is:

1. select source folders,
2. select target folder,
3. choose operation mode,
4. review duplicates,
5. confirm cleanup summary and execute cleanup,
6. choose sorting structure,
7. execute sorting,
8. choose rename structure,
9. execute renaming,
10. optionally enter trip/session grouping,
11. show final congratulations summary.

This order is now the canonical flow target.

---

## 4. Step details

### 4.1 Select source folders

The workflow should first ask for source folders.

The app may already begin background scanning and file counting as soon as source folders are known.

### 4.2 Select target folder

The workflow should then ask for the target folder.

The target should later become the anchor for:

- workflow state,
- hidden project database,
- resuming later work,
- later reuse of prior decisions.

### 4.3 Choose operation mode

The app should ask whether files should be:

- copied,
- moved,
- later possibly deleted in targeted cleanup contexts.

The UI should clearly say that the mode can still be changed later.

---

## 5. Duplicate stage target

### 5.1 Exact duplicate stage

After the initial setup, the workflow enters duplicate handling.

Important UX target:

- the app has already started doing background work,
- but the first visible duplicate step may still present a fake or staged "Start" action,
- results may appear with slight pacing so the experience feels alive rather than instantly dumping a finished table.

### 5.2 Duplicate table target

The duplicate table should later show at least:

- filename,
- format,
- size,
- date,
- number of duplicates,
- similarity / confidence,
- actions.

### 5.3 Duplicate actions target

A duplicate detail or popup view should support:

- previewing one or more candidates,
- keep selected,
- delete selected,
- delete all except one,
- go back,
- clear hint that this is not yet the final advanced comparison tool.

### 5.4 Similarity thresholding

The duplicate pipeline should distinguish:

- 100% exact duplicates,
- high-confidence likely duplicates,
- lower-confidence possible duplicates.

Initial lower bound target for user review lists:

- do not go below about 50% similarity,
- visually separate the safer range from the uncertain range,
- around 70% the app should already communicate increased uncertainty.

### 5.5 Associated file handling in duplicate stage

If related files are detected around a main asset, the app should try to preserve or move them together.

When confidence is too low, the app should:

- say so,
- recommend the user review manually,
- optionally place uncertain sidecar/related files into clearly named fallback folders.

### 5.6 Preview limits

If a file format cannot be previewed in-app:

- show fallback thumbnail if possible,
- otherwise show an honest preview limitation message,
- still communicate that exact duplicate certainty remains valid if hashing proved it,
- offer external open in the default system application.

---

## 6. Cleanup confirmation stage

Once duplicate decisions are complete, the workflow should show a large centered cleanup summary.

It should present:

- scanned file count,
- duplicate count,
- unknown file count,
- recognized associated-file count,
- estimated saved storage,
- selected action mode,
- what will happen next.

The storage-saving number should later be animated.

The main CTA should be a cleanup execution action.

### Dry-run review target

Before final execution, the user should be asked whether to run a dry-run first.

If yes, a readable review window should show:

- every affected file,
- planned action,
- reason,
- ability to sort/filter,
- ability to inspect and adjust a specific item.

---

## 7. Sorting stage target

After cleanup, the user reaches the sorting stage.

### Sorting model target

The default recommendation is a three-level structure such as:

- year,
- month,
- day.

But the structure must be configurable.

The user should be able to:

- add a level on either side,
- remove levels,
- choose from meaningful options per level,
- see a human-readable explanation of the resulting structure.

### Example sorting options

- year (short / full),
- month as number,
- month as written name,
- combined month formats,
- day formats where they are actually meaningful,
- later trip/session layer.

The app should also ask whether the user wants later support for trip/session grouping.

---

## 8. Rename stage target

The rename stage should present:

- centered block-based filename construction,
- predefined templates in a dropdown,
- editable block list,
- add blocks to beginning or end,
- optional original name placement,
- readable examples.

The rename page should feel parallel to the sorting page rather than like a raw technical form.

---

## 9. Trip / session grouping tool target

If the user wants additional trip/session grouping, the workflow continues into a dedicated tool.

### Trip/session workflow target

The user should be able to:

- pick a date range,
- optionally narrow by time,
- see matching media as thumbnails,
- sort by earliest/latest,
- exclude individual files,
- create a trip/session,
- choose whether matching files are moved, copied, or linked,
- revisit and edit the grouping later,
- automatically remove folders that became empty as a result.

This tool should also be available manually outside a workflow.

If it is opened manually, the app should recommend running the main workflow first unless prior workflow state for that folder is already known.

---

## 10. Final summary target

At the end, the app should show a congratulations summary page with:

- total scanned files,
- duplicates handled,
- files sorted,
- files renamed,
- storage saved,
- associated files handled,
- trip/session groups created if applicable.

Later, a small donation entry point can be added there.

---

## 11. Persistence target

The workflow should later store hidden app metadata inside the target structure.

That metadata should allow the app to:

- recognize previously optimized targets,
- compare current state with stored state,
- resume decisions,
- continue a later cleanup pass,
- reuse workflow knowledge instead of starting from zero.

This persistence layer should be treated as mandatory architecture, not a nice-to-have.
