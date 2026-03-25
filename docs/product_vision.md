# Product Vision

## Positioning

Media Manager is intended to become a free public desktop application for people who want to clean, deduplicate, organize, and rename large personal media libraries with a guided workflow and a strong visual UX.

The product target is **not** a developer tool with a thin UI. It is a guided end-user application with a polished desktop experience, clear decisions, recoverable progress, and strong support for mixed photo and video libraries.

## Core product promise

The user should be able to:

1. understand the current problem quickly,
2. start a guided workflow from the home page,
3. review exact duplicates safely,
4. review likely duplicates visually,
5. clean the library without losing track of decisions,
6. sort the result into a flexible folder structure,
7. rename files with readable templates,
8. optionally create trip/session groupings,
9. resume the workflow later if the app closes or crashes.

## UX direction

The intended design direction is:

- modern desktop product UI,
- strong whitespace and hierarchy,
- large central actions,
- minimal cognitive load,
- guided workflow first,
- manual tools second,
- bilingual UI with English as default and German as secondary language,
- later visual language closer to a premium consumer app than a utility panel.

## Platform direction

The preferred future UI stack is **QML / Qt Quick** with Python backend logic.

Reason:

- modern animated desktop UX,
- later Windows `.exe` packaging remains realistic,
- stronger layout and transition control than classic widget UI,
- better fit for a guided product experience.

## Product pillars

### 1. Guided workflow first

The home page should primarily exist to start a guided workflow.

Manual tools remain available in the side navigation, but they are secondary. The app should gently push users toward guided workflows whenever that leads to better results and fewer mistakes.

### 2. Safe cleanup with strong review

Duplicate handling must separate:

- **exact duplicates** (100% byte-identical),
- **likely duplicates / similar captures** (for example several shots of the same subject).

Exact duplicates may be processed faster and more aggressively, but similar media must remain review-driven.

### 3. Large-library stability

The system must remain stable on large libraries up to very high file counts and potentially around 1 TB scale. This requires background indexing, incremental progress, persistence, and resumability.

### 4. Friendly but honest handling of uncertainty

The app should:

- clearly say when a file match is guaranteed,
- clearly say when a match is only likely,
- clearly say when associated sidecar/support files were detected with uncertainty,
- allow the user to continue safely anyway.

### 5. Media-native experience

The app is not only about filenames. It should become a media review environment.

That includes:

- image preview,
- video preview or at least thumbnail preview,
- large compare screens,
- external-open fallback when in-app preview is not possible,
- later trip/session grouping.

## Functional scope target

### Existing or near-term baseline

- guided home page,
- duplicates tool,
- organize tool,
- rename tool,
- exact duplicate detection,
- multiple source folders,
- one target folder,
- dry-run and apply modes,
- persistent app settings.

### Mid-term target

- visual duplicate review,
- likely-duplicate comparison workflow,
- workflow state persistence in a hidden workspace database,
- progress recovery,
- richer folder sorting rules,
- richer rename block system,
- associated-file handling,
- trip/session organizer.

### Longer-term target

- stronger preview engine,
- more file-format coverage,
- donation entry point,
- polished public release packaging,
- installer and signed releases.

## Associated file handling target

Many camera, drone, and editing workflows create related files next to image/video assets.

Examples include:

- RAW + JPEG pairs,
- sidecar files,
- vendor-specific metadata files,
- auxiliary files created next to videos.

The product goal is:

- try to detect related files,
- explain when confidence is low,
- preserve them with the chosen main asset when possible,
- allow separate handling when needed,
- avoid pretending certainty where none exists.

## Persistence and resumability target

Workflows should be stored in hidden application data inside the selected target structure.

The app should later be able to:

- detect that a target was already processed before,
- reload the saved state,
- check whether the files still match the prior known state,
- continue from the saved workflow where possible,
- keep manual review decisions durable.

## Non-goals for now

The following should **not** be treated as immediate build scope for the next small patches:

- final Apple-level visual polish,
- final image/video compare engine,
- all file formats at once,
- all sidecar/vendor rules at once,
- remote multi-user server mode.

These remain target directions, not immediate deliverables.

## Immediate strategic rule

From this point onward, UI work should move toward the product target above instead of continuing to polish the old widget layout incrementally without a clear destination.
