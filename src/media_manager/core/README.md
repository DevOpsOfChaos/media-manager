# Staged Core Package

This directory introduces the rebuilt core structure in a controlled way.

## Why this exists

The repository still contains older flat modules such as organizer-, rename-, duplicate-, and GUI-related code.

A hard big-bang move would create unnecessary churn and make the reset harder to review.

This staged namespace allows the new architecture to start growing immediately while the remaining legacy and transitional modules are still being sorted out.

## Intended direction

The rebuilt core should grow here first:

- scanner
n- metadata
- date_resolver
- organizer
- state
- reporting
- workflows
- utils

## Important rule

New foundational work should prefer this staged core area instead of extending desktop-first legacy surfaces.
