# Workflow State and Persistence Specification

This document defines how the product should preserve progress, decisions, and target knowledge across sessions.

It is a target architecture document.

---

## 1. Why persistence is mandatory

The intended workflow includes:

- large scans,
- staged duplicate review,
- manual decisions,
- sorting and renaming setup,
- optional trip/session grouping,
- later re-entry into previously optimized targets.

Without persistence, the product will feel fragile and untrustworthy.

Therefore workflow persistence is not a nice-to-have feature. It is a required architecture layer.

---

## 2. Storage location target

The product should store workflow state inside the selected target structure using hidden application data.

Examples of stored data:

- workflow database,
- configuration snapshots,
- review decisions,
- file identity references,
- target history,
- trip/session definitions.

The hidden storage should be easy for the app to find again but unobtrusive to normal users.

---

## 3. Core persistence goals

The system should later support:

1. crash-safe recovery,
2. app-close recovery,
3. reopening of previously optimized targets,
4. reuse of prior user decisions,
5. verification that current on-disk state still matches the saved workflow model,
6. safe continuation after partial execution.

---

## 4. Required persisted concepts

### 4.1 Workflow session

A workflow session record should describe:

- session id,
- selected problem type,
- created timestamp,
- last updated timestamp,
- current step,
- current execution state,
- selected source folders,
- selected target folder,
- selected action mode,
- whether trip/session support was requested.

### 4.2 File inventory baseline

The app should persist a baseline inventory model for the workflow.

That model should later be able to answer:

- which files were discovered,
- which were exact duplicates,
- which were likely duplicates,
- which were unknown,
- which were associated files,
- which files were already moved / copied / deleted / renamed.

### 4.3 Duplicate decisions

Duplicate review decisions must be durable.

Persisted duplicate decision data should later include:

- candidate file ids,
- match type (exact vs likely),
- similarity score if applicable,
- user decision,
- decision reason,
- timestamp,
- whether the decision was applied.

### 4.4 Action plan

The execution plan should later exist as its own stored layer.

That plan should include:

- planned file actions,
- action reason,
- target path if applicable,
- whether the action is still pending,
- whether it succeeded,
- whether it failed,
- retry information.

### 4.5 Sorting / rename configuration

Sorting and rename choices must also persist, including:

- selected sort structure,
- selected rename template,
- custom block configuration,
- user overrides,
- last previewed state,
- last applied state.

### 4.6 Trip / session definitions

Trip/session grouping should later persist:

- trip/session id,
- user-visible name,
- selected date range,
- selected time filter,
- included files,
- excluded files,
- mode (move / copy / link),
- current resolved target.

---

## 5. Reopening an already optimized target

When the user selects a target that was processed before, the app should:

1. detect the hidden workflow data,
2. load the prior state,
3. compare the stored model against the current on-disk state,
4. decide whether the target is still trustworthy as a continuation base,
5. offer to continue, re-check, or rebuild.

This should make it possible to run cleanup on an already optimized target again without losing historical context.

---

## 6. Validation targets when reopening

The app should later validate at least:

- whether core files still exist,
- whether action results still match expected target paths,
- whether hidden metadata is intact,
- whether major file counts have drifted,
- whether renamed files still match prior identity assumptions.

When validation fails badly, the app should not silently continue on stale assumptions.

---

## 7. Relationship to manual tools

Manual tools should reuse the same persistence layer.

That means:

- manual mode is not a separate architecture,
- manual operations should still register against workflow state when relevant,
- the app should know whether a directory has prior workflow history,
- manual tools should benefit from prior inventory and decisions where possible.

---

## 8. User trust rules

The persistence layer should always favor trust over cleverness.

Rules:

- never silently discard important review decisions,
- never claim resume certainty if validation is weak,
- always explain when the app is rebuilding from partial data,
- keep the user’s explicit decisions more stable than app-generated guesses.
