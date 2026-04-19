# Support

## Current support reality

This project is still pre-release software.

That means support is best-effort and focused on **reproducible, concrete problems** in the current CLI/Core product direction.

The repository is no longer only a reset skeleton. It now has active functionality around media inspection, organization, renaming, duplicate review, workflows, workflow profiles, and profile bundles. Support requests should match that reality and still be specific.

## Good support requests

Good requests usually include one of these:

- a reproducible bug in a current CLI/Core command
- a clear documentation gap
- a regression after updating to a newer `main`
- a workflow/profile/bundle behavior mismatch with expected output
- path-handling or Windows-specific problems

## Weak support requests

These are much harder to act on:

- vague complaints without commands or reproduction steps
- requests to debug a private media library without logs or examples
- very broad "please make this more professional" requests
- GUI-first feature demands that skip the current product priorities

## Before asking for help

Please include:

- operating system
- Python version
- whether ExifTool is installed
- the exact command you ran
- the full output, traceback, or failing JSON snippet
- whether the problem happened in preview or apply mode
- whether run logs, journals, workflow profiles, or bundles were involved
- whether you are on a recent `main`

## Recommended issue structure

A strong bug report often looks like this:

1. **Command** you ran
2. **Expected behavior**
3. **Actual behavior**
4. **Environment**
5. **Relevant output**
6. **Minimal reproduction** if possible

## Where to ask

- Bugs: open a GitHub issue with clear reproduction steps
- Feature requests: open a focused issue with a concrete use case
- Documentation problems: open an issue or pull request
- Security issues: follow `SECURITY.md`

## Language

Use **English** for public issues and pull requests unless the topic is explicitly about localization.

## Scope note

Support currently focuses on the active architecture direction:

- CLI and core commands
- reporting and history behavior
- workflow presets, profiles, and bundles
- Windows-first usability

Older legacy code may still exist in the repository, but it is not the main support target.
