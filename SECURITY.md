# Security Policy

## Supported versions

Because the project is still pre-release software, only the latest state of the `main` branch should be treated as supported.

## What kinds of issues matter here

Security-relevant reports can include things like:

- unsafe deletion or overwrite paths
- path traversal or unsafe file-write behavior
- dangerous profile/bundle import or extraction behavior
- command execution paths that accept untrusted input unsafely
- accidental exposure of sensitive local paths or data in logs/reports

This is primarily a local-media management tool, so the most important security concerns are usually **file safety**, **path safety**, and **unexpected destructive behavior**.

## Reporting a vulnerability

Do **not** open a public issue for security-sensitive findings.

Use GitHub private reporting features if available, or contact the maintainer privately through the repository profile.

Include:

- a clear description of the issue
- reproduction steps
- expected impact
- environment details
- proof of concept, if it is safe to share
- whether the issue affects preview mode, apply mode, or both

## What to avoid in a report

Please do not include:

- private media files unless absolutely necessary
- secrets or tokens
- full personal library dumps
- exploit details that would unnecessarily expose users before a fix exists

## Response expectations

No formal response SLA is guaranteed at this stage.

The best reports are the ones that are:

- concrete
- reproducible
- scoped
- written against the latest `main`
