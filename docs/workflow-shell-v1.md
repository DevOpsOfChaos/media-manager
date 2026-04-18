# Workflow Shell v1

`media-manager workflow` is a guided entry point for the command-line product.

It does not replace the existing commands.
It sits above them and helps users answer these questions:

- Which workflow fits my problem?
- What does this workflow actually do?
- What command should I run next?
- Can I start the chosen workflow from one central place?

## Supported shell commands

- `media-manager workflow list`
- `media-manager workflow show <workflow>`
- `media-manager workflow problems`
- `media-manager workflow recommend <problem>`
- `media-manager workflow run <workflow> ...`

## Current workflows

v1 exposes the existing workflow-oriented commands from one central entry point:

- cleanup
- trip
- duplicates
- organize
- rename

## Why this matters

The project goal is not only to expose isolated commands.
It is also to offer guided problem-first flows such as:

- messy multi-source cleanup
- trip collections
- duplicates-first review

This shell is the first explicit CLI step in that direction.

## Non-goals in v1

- no GUI
- no interactive terminal wizard yet
- no persistent workflow history yet
- no hidden magic execution layer

v1 keeps the behavior honest:
it explains workflows and delegates to the real commands.
