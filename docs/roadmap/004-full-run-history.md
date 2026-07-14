# 004: Full run history

**Status:** Proposed

## Problem

`RecordsManager` currently only keeps the best time per floor and the
best total time, overwriting previous bests. There's no way to review
past runs — only the current record. A (usually hidden) panel should
let users browse the full history of floor times and total times
across all runs, not just the fastest one.

## Proposed design

_To be refined._

## Open questions

- Data format: extend `zarokh_records.json`, or a separate file/table
  for history (e.g. `zarokh_history.json`)? Given the file could grow
  unbounded, is there a retention policy (keep last N runs)?
- Migration: existing `zarokh_records.json` files in the wild don't
  have this data — how do we handle upgrading a user's existing file
  without losing their current records?
- UI: what does the hidden panel look like — a scrollable list, a
  table, sortable/filterable?
- Relationship with [002](002-simplified-auto-mode-ui.md) and
  [005](005-unique-relic-tracking.md): each history entry will likely
  need to store relic data (005) once that's designed.

## Status log

- 2026-07-14: Proposed.