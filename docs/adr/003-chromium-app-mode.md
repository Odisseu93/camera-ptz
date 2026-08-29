# ADR 003: Chromium Application Mode Launching

## Context
When web server mode is started locally, the user may want an automated browser view without opening a bloated multi-tab browser session.

## Decision
Launch Chromium in `--app=http://localhost:PORT` mode with minimal memory flags (`--disable-gpu`, `--disable-extensions`, `--js-flags="--max-old-space-size=128"`).

## Consequences
- Eliminates browser UI chrome (address bar, bookmarks, tabs), saving screen real estate.
- Constrains browser memory consumption to ~100-150MB.
