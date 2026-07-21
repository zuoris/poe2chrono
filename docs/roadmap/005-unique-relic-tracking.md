# 005: Unique relic tracking per run

**Status:** Designed

## Problem

Users should be able to record how many of the five unique relics
were obtained during each run:

- The Last Flame
- The Desperate Alliance
- The Burden of Leathership
- The Changing Seasons
- The Peacemaker's Draught

## Proposed design

### Where it lives

Extends the run history window added by
[004 (Full run history)](004-full-run-history.md): one additional
column per relic, added to the existing per-run rows.

### Pinned header rows

The history window's pinned area grows from one row to two:

1. **Relic totals row** (new): sum of each relic's count across all
   of history. Recalculates immediately whenever a count is edited.
   Floor/total time columns are blank here — totals don't apply to
   times.
2. **Best times row** (existing "PB" row): unchanged, shows the
   floor/total time records. Relic columns are blank here — a "best"
   doesn't apply to relic counts.

The relic totals row sits directly above the best-times row, so both
pinned rows stack immediately below the column headers.

### Editing

- Each relic cell has small **+/- stepper buttons** to increase or
  decrease that run's count for that relic.
- **Only completed runs are editable.** Cancelled runs never had a
  Zarokh kill, so no relic could have dropped — their relic cells
  show no steppers (e.g. blank/disabled).
- **Minimum 0, no maximum.** The `-` button has no effect (or is
  disabled) once a relic's count for that run reaches 0.

### Storage

Each completed run's entry in `zarokh_data.json`'s `runs` list gains
a `relics` field: a mapping from relic name to count, defaulting to
0 for all five relics. Cancelled run entries don't get a `relics`
field at all (there's nothing to edit). Exact key naming (full relic
name vs. a short slug) to be settled during implementation.

## Status log

- 2026-07-14: Proposed.
- 2026-07-20: Refined — relic names confirmed, location (history
  table) and editability confirmed. Interaction mechanism, totals
  placement, and storage shape still open.
- 2026-07-20: Designed — all open questions resolved: totals row
  pinned above the best-times row, +/- stepper buttons, completed
  runs only, floor 0 with no ceiling.
- 2026-07-21: Implemented. Run list rebuilt with hand-made rows
  instead of Treeview to support per-cell +/- buttons. History
  window resizes to fit content. Older history entries (pre-dating
  this feature) are backfilled with zeroed relic counts on load.
