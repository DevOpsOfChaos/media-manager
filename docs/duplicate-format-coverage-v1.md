# Duplicate and format coverage hardening v1

This update makes the backend support boundary more explicit.

## What changed

- media-format capabilities are now defined from one central module
- exact-duplicate support and similar-image support are no longer treated as the same thing
- common alias formats such as `.jfif`, `.jpe`, `.m4v`, `.mpg`, and `.mpeg` are now covered explicitly
- HEIC/HEIF and RAW-family files remain part of the general media/exact-duplicate pipeline
- similarity scanning stays intentionally narrower and decoder-safe by default

## Why this matters

The project should not pretend that all media formats have the same level of support.

For example:

- byte-level exact duplicate detection can safely work for many formats as long as the files are scanned
- perceptual similarity needs reliable image decoding and should therefore stay more conservative

That distinction makes the CLI more honest and easier to harden before a later GUI uses the same backend.

## Current support model

### Exact duplicate pipeline

The exact-duplicate pipeline is intended to cover all supported media extensions collected by the scanner.
It works at the byte level and is therefore broader than perceptual image similarity.

### Similar image pipeline

The similar-image pipeline is intentionally limited to image formats with stable decoder expectations in the current dependency set.
Formats such as HEIC/HEIF and RAW variants are not enabled there by default.

## Direction after this block

The next hardening steps should focus on:

- more real-world duplicate regression coverage
- date-resolution hardening
- organize/rename idempotence hardening
- clearer CLI reporting of support boundaries and blocked actions
