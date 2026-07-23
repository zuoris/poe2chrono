# 009: Unify main and history windows into a single window

**Status:** Designed

## Problem

Having two independent windows (the compact timer overlay and the
separate run history window) is confusing for the user. Zarokh
should be a single window.

## Proposed design

- One `Tk` root hosting one frame per screen, shown/hidden as
  needed (simple pack/pack_forget swapping — no virtualization or
  optimization needed given the current data volume).
- Two screens exist after this item: **Run** (clocks, deltas,
  Pause/Restart/Cancel) and **Post-Run** (the current history
  window's content: relic totals row, PB row, run list with relic
  editing).
- **The Run screen's hidden "+" panel is removed entirely.** Its
  floor-best/PB-total labels were redundant with the PB row already
  shown on Post-Run, so they're simply dropped rather than
  duplicated. What used to open that panel (the "+/-" button) is
  replaced by a single button that navigates straight to Post-Run,
  using an icon that suggests a history/archive instead of "+/-".
- **Clear Records moves to the Post-Run screen** — it belongs with
  the records it clears, not tucked inside Run.
- **A "Back" button on Post-Run returns to Run.** This is a
  deliberately temporary affordance: with only two screens right
  now, a single button is enough. It gets superseded once
  [010](010-navigation-menu.md) introduces the real navigation menu.
- **Always-on-top stays on for the single window** — this resolves
  the conflict between the old Timer (always-on-top) and History
  (not always-on-top) by picking one consistent behavior.
- **New: a minimize button**, placed immediately to the left of the
  close button, so the user can get the always-on-top window out of
  the way if it's ever in the way.
- The win32 taskbar-forcing hack, window dragging, and the close
  button — currently duplicated in both windows — are unified into
  one place.
- The window resizes to fit its content (`_resize_to_content()`)
  every time the active screen changes, not just on initial launch.

## Status log

- 2026-07-23: Proposed as part of the original (too broad) item 009.
- 2026-07-23: Designed — split into a standalone item, minimize
  button and always-on-top resolution confirmed.
- 2026-07-23: Refined — Run's hidden "+" panel removed entirely (its
  content was redundant with Post-Run's existing PB row); Clear
  Records moves to Post-Run; the former "+/-" button becomes a
  direct history-icon shortcut to Post-Run; Post-Run gets a
  temporary "Back" button until 010 lands.
