# QML Implementation Plan

This document defines how the QML migration should progress from the current preview shell to the target workflow product.

---

## 1. Immediate rule

The QML path is now the forward-looking UI path.

The older widget UI remains useful as fallback while the QML implementation matures, but new UX investment should primarily strengthen the QML version.

---

## 2. Migration principle

The migration should not be attempted as one giant rewrite.

The safer path is:

1. build the shell,
2. replace one workflow stage at a time,
3. move supporting logic behind stable interfaces,
4. retire widget pages only when equivalent QML pages are genuinely usable.

---

## 3. Current QML stage

The current QML work should be treated as:

- shell foundation,
- navigation baseline,
- language toggle baseline,
- home landing page baseline,
- workflow stage preview baseline,
- bottom status bar baseline.

It is not yet the finished workflow.

---

## 4. Recommended implementation order

### Phase A — make the shell real

1. finalize the landing page composition,
2. finalize the workflow shell layout,
3. make the bottom bar persistent and realistic,
4. make stage transitions feel consistent.

### Phase B — source and target stages

1. proper source-folder selection,
2. proper target-folder selection,
3. live scan progress based on real work,
4. stage confirmations and navigation.

### Phase C — duplicate stage

1. wire real exact duplicate data into the staged duplicate list,
2. show progress from real pipeline state,
3. open a first real review popup,
4. support keep/delete decisions,
5. persist decisions.

### Phase D — compare stage

1. target-vs-source compare view,
2. media previews,
3. external-open fallback,
4. confidence-range separators,
5. associated-file hints.

### Phase E — cleanup execution stage

1. cleanup summary page,
2. dry-run plan viewer,
3. action editing,
4. execution progress,
5. persistence of applied state.

### Phase F — sorting and rename stages

1. folder-structure builder,
2. rename block builder,
3. presets,
4. previews,
5. execution feedback.

### Phase G — optional trip/session stage

1. date/time filter view,
2. thumbnail review,
3. include/exclude controls,
4. trip/session persistence,
5. edit existing trips/sessions.

---

## 5. Architectural boundary target

The QML layer should stay focused on:

- presentation,
- staged interaction,
- progress state,
- user decisions.

The Python backend should own:

- scanning,
- metadata extraction,
- hashing,
- duplicate detection,
- similarity matching,
- action planning,
- persistence,
- execution.

The QML frontend should consume structured state instead of reimplementing file logic.

---

## 6. Immediate next coding priorities

The best next code priorities are:

1. make the QML home page match the intended premium landing-page layout,
2. wire real source/target selection into the QML workflow,
3. replace fake live counters with real background state,
4. replace fake duplicate rows with real duplicate preview data,
5. keep the widget app as fallback until those steps are stable.
