# 006: Abandoned and interrupted runs

**Status:** Proposed

## Problem

In Sekhemas, a player can leave a run in two different ways:
- **Leave for good** — the run is abandoned and won't be resumed.
- **Leave temporarily** — the player exits but may resume the same
  run later.

The app currently has no concept of this distinction. This item was
split out from [002 (Simplified auto-mode UI)](002-simplified-auto-mode-ui.md),
where it was identified as out of scope for that design. For now,
floor times keep being recorded as each floor completes, and the
explicit Cancel action (see 002) is the only way a run is discarded.

## Proposed design

_To be refined. Likely to be split into two separate items — one for
abandoned runs, one for temporarily interrupted runs — once each is
better understood._

## Open questions

- How does the app detect (via game log or otherwise) that a run was
  left temporarily vs. abandoned for good, as opposed to relying only
  on the explicit Cancel button from 002?
- How does this interact with [001 (Run attempt counter)](001-run-attempt-counter.md)
  and [004 (Full run history)](004-full-run-history.md): does an
  abandoned or interrupted run count as an "attempt", and how is it
  represented in history?
- What happens to floor records already saved for a run that later
  gets abandoned or interrupted?

## Status log

- 2026-07-14: Proposed, split out from item 002.
