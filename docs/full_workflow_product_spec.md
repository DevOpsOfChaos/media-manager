# Full Workflow Product Specification

This document translates the target product vision into a concrete guided workflow for the primary user path.

It describes the intended end-state. It does not claim that every part is already implemented.

---

## 1. Product intent

The main workflow is the primary user experience of Media Manager.

The app should not feel like three separate utility panels glued together. It should feel like one guided premium desktop workflow that helps the user:

1. understand their current problem,
2. choose the right cleanup path,
3. review and resolve duplicates safely,
4. sort the remaining library into a better structure,
5. rename the cleaned result in a readable way,
6. optionally create trip/session groupings,
7. finish with a clear summary of what was achieved.

The canonical full path remains:

1. Duplicates
2. Organize
3. Rename
4. Optional trip/session sorting

---

## 2. Home page target

The home page should be built like a product landing page rather than a tool launcher.

### Required structure

- very large centered product title,
- large central questionnaire block,
- four large stacked problem buttons,
- very short and readable problem statements,
- dismiss action centered below the questionnaire,
- explanatory section below the questionnaire,
- side menu remains available but secondary.

### Problem choices

The user selects one of four starting situations:

1. full cleanup,
2. duplicates already handled, now organize,
3. already organized, mostly rename,
4. exact duplicate review only.

Clicking one option should immediately enter the workflow.

### Dismiss behavior

When dismissed:

- the large questionnaire disappears,
- the informational section remains,
- one restart action appears below.

---

## 3. Global workflow shell

After a problem is chosen, the workflow becomes the main stage.

The workflow should be presented as a sequence of large app-like pages instead of crowded utility forms.

### Global shell requirements

Every step should later share:

- a large centered main content area,
- one clear back action in the lower left,
- one bottom status / information bar,
- visible progress indication,
- subtle animation,
- compact but clean base size,
- graceful scaling upward when the window is enlarged.

### Bottom status bar

The bottom bar is persistent across all workflow steps.

It should show:

- source directory count,
- selected target directory,
- selected operation mode,
- current step and remaining steps,
- live discovered media count,
- rotating tips and fun facts.

The rotating content should include:

- photography facts,
- file management advice,
- historical camera / media facts,
- positive reinforcement about cleanup progress.

This is intended to feel similar to a polished loading/status strip rather than a debug panel.

---

## 4. Full workflow step sequence

### Step 1 — Select source folders

This is the first mandatory step in the full workflow.

Requirements:

- support multiple source folders,
- present a large central action,
- confirm selection visually,
- immediately start background scanning and counting once sources are known.

### Step 2 — Select target folder

After sources are selected, ask for the target folder.

Requirements:

- large centered stage,
- clear confirmation after selection,
- target later acts as the home of hidden workflow state and databases.

### Step 3 — Choose file action mode

Ask what should happen to files overall.

Current intended choices:

- copy,
- move,
- delete in selected cleanup contexts.

The page must clearly say that this can still be changed later.

### Step 4 — Exact duplicate review stage

Once sources and target are known, the duplicate pipeline is already working in the background.

The visible duplicate stage may still expose a large Start button, but this is mostly a UX gate for the visible review phase rather than the true beginning of computation.

#### Intended visible behavior

- large stage title,
- animated progress bar,
- duplicate rows appearing gradually rather than instantly,
- staged reveal to keep the workflow feeling alive.

#### Initial duplicate table target

The duplicate review table should show at least:

- file name,
- format,
- size,
- date,
- duplicate count,
- similarity / confidence,
- actions such as show / inspect.

#### Duplicate popup / quick review target

When the user clicks a duplicate item, a foreground review window should open.

The popup should later allow:

- showing all duplicate candidates,
- selecting one candidate,
- delete selected,
- keep selected,
- delete all except one,
- go back,
- a hint that this is still not the final advanced compare tool.

#### Exact vs likely duplicate separation

The workflow must clearly distinguish:

- 100% exact duplicates,
- likely duplicates,
- low-confidence similar captures.

Sorting should be highest confidence first.

The long-term review floor should not go below around 50% similarity, and the UI should visually separate the range where confidence falls below about 70%.

### Step 5 — Target-vs-source comparison stage

After the exact duplicate stage, the workflow moves into a stronger compare screen.

The intended layout is:

- two preview areas above,
- left side showing current source candidate(s),
- right side showing chosen target result,
- left table wider and richer,
- right table narrower and more final.

Required comparison information:

- full name,
- size,
- date,
- similarity,
- count of related matches,
- target status.

Media preview must support:

- images,
- videos where possible,
- enlarging previews,
- not overgrowing the viewport,
- obvious close affordance such as an X,
- external-open fallback.

### Step 6 — Cleanup summary and execution

Once duplicate decisions are complete, show a centered summary page.

It should explain:

- total scanned files,
- duplicate count,
- unknown file count,
- related / associated files detected,
- what happened to those associated files,
- chosen action mode,
- estimated saved storage.

The saved-storage number should later be animated.

A main cleanup CTA should be present.

#### Dry-run review

Before execution, the user should be offered a dry-run preview.

The dry-run window should later show:

- every affected file,
- action to be taken,
- reason for the action,
- sorting / filtering by action,
- ability to inspect and adjust a selected row.

### Step 7 — Sorting stage

Once cleanup is accepted, the workflow goes to folder structure setup.

The default recommendation is a three-level structure such as:

- year,
- month,
- day.

But the system must support richer composition.

The user should be able to:

- add levels on either side,
- remove levels,
- choose meaningful format options per level,
- preview the resulting structure conceptually.

Examples of level options:

- year in different display forms,
- month as number,
- month as full name,
- combined month formats,
- day labels where appropriate.

At this stage the app should also ask whether the user wants later support for trip/session grouping.

### Step 8 — Rename stage

After sorting, the workflow reaches rename setup.

The rename UI should later provide:

- centered block-based filename construction,
- preset templates,
- editable block list,
- add block at the beginning or end,
- optional original name at beginning or end,
- readable examples.

Examples of presets:

- year month day time readable,
- year full-month day time readable,
- date time original stem,
- date + sequence + original stem.

### Step 9 — Optional trip / session stage

If trip/session help was requested earlier, the workflow continues into a dedicated trip tool.

The user should later be able to:

- choose a date range,
- narrow further by time,
- preview matching media as thumbnails,
- sort by first/last,
- exclude individual files,
- decide whether files are moved, copied, or linked,
- save and later edit the trip/session,
- automatically remove emptied folders if desired.

This tool should also be manually accessible, but when entered manually it should advertise the main workflow unless prior workflow state is already known for the selected target.

### Step 10 — Final congratulations page

The workflow ends with a final summary page that celebrates progress and lists:

- files scanned,
- duplicates handled,
- files sorted,
- files renamed,
- storage saved,
- unknown files,
- associated files handled,
- trip/session groups created if applicable.

A donation entry point may later live here.

---

## 5. Associated files behavior target

Many cameras, drones, and media tools create related files around the main photo or video.

Examples include:

- RAW + JPEG pairs,
- sidecar metadata files,
- manufacturer-specific support files,
- video support files.

The workflow should try to:

- detect associated files,
- preserve them when confidence is high,
- explain uncertainty when confidence is low,
- allow placing uncertain files into a structured fallback folder,
- avoid pretending certainty when it cannot guarantee correctness.

The product goal is user trust, not fake cleverness.

---

## 6. Preview and format support target

The product should support as many image and video formats as practical.

If in-app preview is not possible:

- try thumbnail preview,
- otherwise show an honest preview limitation state,
- still preserve duplicate certainty where hashing guarantees it,
- allow external open in the default application.

---

## 7. Manual tools alignment

The manual tool pages remain available.

But they should gradually inherit the logic and design language of the workflow.

They should not evolve into a second inconsistent product.

Manual entry should:

- reuse workflow logic where possible,
- ask for sources and target if opened standalone,
- recommend the guided workflow when appropriate,
- skip that recommendation when the app already knows that the target has prior workflow state.
