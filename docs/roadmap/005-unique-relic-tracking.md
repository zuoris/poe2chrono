# 005: Unique relic tracking per run

**Status:** Proposed

## Problem

Users should be able to edit a completed run afterwards to record how
many of the four unique relics were obtained during that run:
- The Last Flame
- The Desperate Alliance
- (two more — names to be confirmed)

## Proposed design

_To be refined._

## Open questions

- Confirm the names of the remaining two unique relics.
- This depends on [004 (Full run history)](004-full-run-history.md)
  existing first, since there needs to be a persisted, identifiable
  run to edit — a "best time" record alone doesn't have enough
  identity (e.g. no timestamp) to attach relic data to.
- UI: how does a user select a specific past run to edit? Where does
  the edit action live?
- Data: relic count per relic (0-1, since presumably at most one of
  each per run), or a simple checklist?

## Status log

- 2026-07-14: Proposed.