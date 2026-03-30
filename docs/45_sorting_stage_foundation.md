# Sorting Stage Foundation

## Why this is the next step

The current workflow already includes:
- source selection
- target selection
- operation mode
- exact duplicate review
- cleanup summary / dry-run foundation

The next meaningful product step is to replace the sorting placeholder with a real sorting builder.

Right now the sorting stage still behaves like a static preview. That is no longer enough once the cleanup summary exists.

## Goal of this milestone

Introduce a clean, testable sorting-core foundation before wiring more UI controls into QML.

This keeps the next visible workflow changes grounded in reusable logic instead of hardcoded labels.

## Scope of the new core module

The sorting foundation should provide:
- structured sort level definitions
- path-part formatting by date/time
- localized month-name support
- preview generation for relative target directories

## Current first supported sort semantics

The initial core supports these level kinds:
- year
- month
- day

And these first styles:
- year: `yyyy`, `yy`
- month: `mm`, `name`, `yyyy-mm`
- day: `dd`, `yyyy-mm-dd`

This is enough to build a real first sorting builder without pretending the full system already exists.

## Why the core comes first

The next QML step should not invent directory strings inline.
It should call a reusable planning layer.

That planning layer should later expand toward:
- more sort level styles
- date-source selection
- unknown-date fallback handling
- target collision handling
- mixed language formatting decisions

## Next visible workflow step

After this core exists, the next UI task is:
- replace the sorting placeholder page with a real sorting configuration stage
- show active sort levels
- allow simple style switching
- generate a visible preview list of resulting target directories

## Out of scope for this milestone

Do not mix these in yet:
- actual file moves for sorting
- rename builder logic
- trip/session grouping
- metadata extraction from EXIF/video containers

Those are later layers.
