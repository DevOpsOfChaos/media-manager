# Organize/Rename Diagnostics + Similar Engine Hardening v2

## Goal

Ship a larger, internally checked core block that improves two adjacent areas at once:

- organize/rename dry-run and execution diagnostics
- similar-image engine diagnostics

## Organize / Rename

The dry-run and execution models now expose structured summaries that are useful for later CLI or GUI presentation:

- status summary
- reason summary
- resolution source summary
- confidence summary
- execution outcome/action summary

This keeps reporting logic close to the core models instead of scattering it through CLI code.

## Similar Image Engine

The similar-image scan now records:

- candidate pair count
- exact perceptual-hash pair count
- decode error count
- original image width / height per member

This makes the similarity stage much easier to debug and review on real-world photo sets.
