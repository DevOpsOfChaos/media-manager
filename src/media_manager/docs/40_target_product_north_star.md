# Target Product North Star

## Purpose

Media Manager should become a free public desktop application for large-scale photo and video cleanup, consolidation, sorting, and renaming with a modern, app-like interface. The preferred UX path is a guided workflow. Manual tools remain available, but they are secondary and should progressively reuse the same core logic as the workflow path.

The primary platform remains desktop with a modern QML / Qt Quick frontend and a Python backend. The UX goal is clean, premium, modern, and calm. The application should feel more like a focused desktop app than a collection of separate tools.

## Strategic Product Position

The product is not just a duplicate finder, not just a sorter, and not just a renamer.

It is a guided media cleanup system with these priorities:

1. Reduce chaos safely.
2. Help the user make good decisions without expert knowledge.
3. Preserve trust through transparency, previews, dry runs, and recoverable decisions.
4. Support large real-world media libraries, not only small clean test folders.
5. Support both images and videos, and as many real-world formats as practical.
6. Treat “related files” seriously enough to avoid destroying workflows around camera and drone media.
7. Keep the workflow alive across restarts by storing hidden workflow state in the target system.

## Product Principles

### Guided first
The home page should push the user into a guided path. Manual tools stay available, but the UI should clearly suggest that the workflow is the intended route.

### One calm screen at a time
The workflow should avoid clutter. Each stage should present one decision domain at a time.

### Large, centered, readable
The core question or action on each page should be large, centered, and immediately obvious. Secondary detail should not overpower the main action.

### Trust by visibility
The user should continuously understand:
- where they are in the workflow
- how many files were scanned
- what mode is currently selected
- what the next decision means
- what the software will do before it does it

### Fake wait is acceptable, fake logic is not
The system may delay visual reveal for better UX, such as gradually inserting already-found duplicate rows. But the actual data pipeline must remain real.

### Safe by default
Dry run, summaries, and reversible decisions should be emphasized. Deletion and destructive actions require clarity and explicit confirmation.

### Modern, not “dashboard-y”
Avoid the old tile/grid mentality. The product should use clean centered layouts, restrained framing, subtle glow/border feedback, and deliberate whitespace. It should not look like a legacy admin panel.

## Supported Media Scope

The target product must explicitly consider:

- common image formats
- common video formats
- RAW and JPEG coexistence
- drone / camera sidecar or manufacturer-adjacent files
- preview limitations for unsupported codecs or formats
- external-open fallback when internal preview is not possible

If something cannot be previewed, the product must say so clearly without undermining confidence in exact-match detection.

## User Value Statement

The application should help users transform messy folders into a clean, structured, trustworthy media library with less stress, less accidental loss, and better long-term maintainability.
