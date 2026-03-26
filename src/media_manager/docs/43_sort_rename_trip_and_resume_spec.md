# Sorting, Renaming, Trip Workflow, and Resume Spec

## Sorting Stage

After cleanup, the user should be guided into sorting.

### Sorting UI
Centered configuration blocks.
Default suggestion:
- Year
- Month
- Day

The user may add or remove levels.
Each level must expose only sensible options.

Examples:
- Year: numeric year, two-digit year only if genuinely needed
- Month: number, full month name, combined forms
- Day: numeric day, weekday forms where useful

The product should avoid pointless options. It should guide, not overwhelm.

### Optional trip/session sorting
The sorting stage should ask whether the user wants additional help grouping:
- vacations
- multi-day trips
- sessions
- day trips

If enabled, the workflow gains an additional later stage.

## Rename Stage

The last standard workflow stage is rename configuration.

### Rename UI
Centered layout again.
The user configures filename building blocks.

Capabilities:
- add blocks at start or end
- include original name
- choose readable date/time blocks
- apply predefined templates from a dropdown
- templates automatically populate the current block list

Examples:
- readable year month day time
- year + full month + day + time
- date + original stem

The UI should make templates feel helpful, not magical.

## Trip / Session Tool

If enabled, the trip/session tool runs after sorting or as a manual tool.

Capabilities:
- choose date range
- optionally refine with time range
- preview matching files as clear thumbnails
- sort by earliest / latest
- exclude single or multiple files
- create trip/session
- choose move / copy / shortcut behavior
- default should be move
- persist created trip definitions for later editing
- delete now-empty folders after reorganization where appropriate

The trip tool should be flexible enough for:
- vacations
- multi-day events
- photo walks
- drone sessions
- any user-defined thematic batch

## Manual Tools

Manual tools remain available but should progressively reuse workflow logic.

If a manual tool is opened outside an existing optimized target:
- require source selection first where relevant
- recommend running the workflow first
- explain why workflow gives better results

If the system detects a previously optimized target:
- reuse existing hidden state
- avoid redundant warning copy
- allow resume / continue / revisit behavior

## Hidden State and Resume

The application should store hidden workflow state within the target system.

Goals:
- resume after crash
- resume after accidental close
- reopen a previously optimized library and continue
- detect whether the target still matches known state
- compare and revalidate before assuming prior state is still valid

The state model should include at least:
- target identity
- workflow stage reached
- user decisions
- duplicate handling results
- related-file handling notes
- dry run history
- execution results
- sorting configuration
- rename configuration
- trip/session definitions if used
- last known scan metadata

## Final Completion Screen

The congratulations screen should summarize what the workflow achieved:
- files scanned
- duplicates resolved
- storage saved
- sorting applied
- rename applied
- trip/session work applied if used

Later, a small support or donation option may be introduced, but it should not dominate the result page.

## Immediate Implementation Priority

Do not attempt to build the full product at once.

Priority order:
1. Stable, clean QML shell
2. Strong home page and navigation direction
3. Clean workflow framing with persistent bottom strip
4. Source / target / mode stages
5. Exact duplicate review with trustworthy state handling
6. Summary + dry run
7. Sorting
8. Renaming
9. Trip/session tool
10. Resume and mature state persistence expansion
