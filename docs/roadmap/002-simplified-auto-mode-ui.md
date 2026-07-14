# 002: Simplified auto-mode UI

**Status:** Proposed

## Problem

In automatic mode (when `Client.txt` is detected and log events drive
the timer), the Start, Floor, and Reset buttons are redundant — the
app already reacts to the game log. Showing them adds visual clutter
and could tempt users to interact in ways that conflict with the
automatic tracking. In automatic mode, only a Pause/Restart control
should be shown.

## Proposed design

_To be refined._

## Open questions

- What does "Restart" do exactly in automatic mode — same as the
  current manual Reset, or something else (e.g. re-sync with the
  current game state)?
- Should switching between manual and automatic mode (via the mode
  indicator button) dynamically show/hide these controls, or is a
  restart of the app required?
- Interaction with `AppController.handle_log_event` and the existing
  play/pause-only behavior for the `START` log event (see
  [decision log](../../areas/zarokh.md) — Start never resets, only
  Reset resets).

## Status log

- 2026-07-14: Proposed.