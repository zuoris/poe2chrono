# 007: Persist application state across executions

**Status:** Proposed

## Problem

If the app is closed while a run is in progress, that run's progress
is currently lost — there's no way to resume it on the next launch.

On an unexpected exit (crash, forced kill), nothing can reasonably be
done. But on a controlled exit, the app should be able to save enough
state to let the user resume where they left off.

## Proposed design

- Rename `zarokh_records.json` to `zarokh_data.json`, and store all
  persisted state there (not just best-time records).
- On a controlled exit, prompt for confirmation before closing.
  Pressing ESC again while the confirmation is showing cancels the
  exit and returns to the app (a loop: ESC shows the prompt, ESC
  again dismisses it and resumes normal operation, rather than
  closing).
- On confirmed exit, persist the current run's state (elapsed times,
  current floor, run status) to `zarokh_data.json`.
- On next launch, detect saved in-progress state and offer to resume
  it.

## Open questions

- File migration: existing users have `zarokh_records.json` — does
  the app rename/migrate it automatically on first launch after this
  change, or is it a clean break?
- What exactly counts as "resumable" state, and how does it interact
  with [002's Cancel button](002-simplified-auto-mode-ui.md) and the
  paused-floor-completion safety net — e.g. if the saved run was
  paused, does resuming put it back in a paused state?
- Relationship with [004 (Full run history)](004-full-run-history.md):
  should in-progress run state live in the same file/structure as
  historical run data, or be kept separate (e.g. a single
  "current run" slot vs. a list of past runs)?

## Status log

- 2026-07-14: Proposed.
