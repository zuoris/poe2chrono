# 004: Full run history

**Status:** Designed

## Problem

`RecordsManager` currently only keeps the best time per floor and the
best total time, overwriting previous bests. There's no way to review
past runs — only the current record.

## Proposed design

### Where it lives

A dedicated window, separate from the main compact overlay — larger,
since there's no need to conserve space for an always-visible
floating timer (no live clock is shown here; history isn't reviewed
mid-run). Unlike the main overlay, this window is **not** always-on-
top — it can sit behind other windows, since it's meant to be
consulted between runs, not while actively playing.

### Layout

- A **record row**, pinned at the top of the window, always visible
  regardless of scroll position. Composed of the best time for each
  floor plus the best total time — the same columns every run row
  uses, so comparison is a direct visual alignment.
- Below it, a **scrollable list of runs**, one row per run, in
  **reverse chronological order (most recent first)**. Columns
  aligned with the record row. About 5 rows visible at once without
  scrolling.
- **First column**: the attempt number, with room for 4 digits. This
  doubles as the resolution for
  [001 (Run attempt counter)](001-run-attempt-counter.md) — no
  separate counter needed, it's just the count of history entries.

### What counts as a run, and what gets recorded

- Both **completed** (Zarokh killed) and **cancelled** runs are
  included in the history — every attempt gets a row.
- A **completed** run shows its total time in the total-time column.
- A **cancelled** run shows `--:--.--` in the total-time column —
  there's no meaningful total for a run that wasn't finished.
- For a cancelled run, the floor columns show the times for whichever
  floors were validly completed before the cancellation; floors past
  the cancellation point are blank.
- A floor time is only ever recorded if it was **valid** — i.e. the
  floor wasn't paused when it was completed. This already matches
  the existing `Run.register_floor()` behavior (it only registers a
  floor while actively running, never while paused), so no extra
  validity check is needed at the history layer: every `FloorResult`
  produced during a run is by construction valid, whether the run
  goes on to finish or gets cancelled afterwards.

### Storage

Extends `zarokh_data.json` (per [007](007-persist-app-state.md)'s
proposed rename from `zarokh_records.json`) with a list of entries,
one per run:

```json
{
  "attempt": 1,
  "floor_times": [45.2, 38.9, 52.1, 60.0],
  "total_time": 196.2
}
```

- `attempt`: sequential run number (1-indexed, never reused).
- `floor_times`: list of valid floor times recorded, in order. May
  have fewer than 4 entries for a cancelled run.
- `total_time`: `null` (or absent) for a cancelled run.

Field names above are a starting proposal, not final — to be
confirmed during implementation.

No cap on the number of stored runs for now; revisit as a separate
item if this ever becomes a real problem.

### Color coding

Deferred to
[008 (Color-coded floor times in run history)](008-color-coded-run-history.md) —
this item ships with every floor time in a single neutral color.

## Status log

- 2026-07-14: Proposed.
- 2026-07-14: Refined — dedicated window (no live clock), pinned
  record row, scrollable run list (~5 visible), per-floor color
  coding proposed.
- 2026-07-14: Designed — all open questions resolved (completed vs.
  cancelled runs, attempt numbering resolving item 001, storage
  structure in zarokh_data.json, non-topmost window). Color coding
  split off into item 008 and deferred.
