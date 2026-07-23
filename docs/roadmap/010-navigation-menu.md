# 010: Navigation menu (Pre-Run / Post-Run)

**Status:** Designed

## Problem

With three screens (Pre-Run, Run, Post-Run), the user needs a
consistent way to move between Pre-Run and Post-Run. The Run screen
is intentionally not reachable from this menu.

## Proposed design

- A persistent navigation menu with two buttons: **Pre-Run** (gear
  icon) and **Post-Run** (an icon suggesting visiting a historical
  archive — exact icon TBD once built and seen on screen, same as
  every other icon in this app so far).
- The menu is shown **only while there's no active run**
  (`Run.state == IDLE`), on both the Pre-Run and Post-Run screens.
- The Run screen never shows this menu. The only way into Run is the
  "Ready" button on Pre-Run ([011](011-create-pre-run-screen.md));
  the only way out is finishing a run (killing Zarokh) or explicit
  Cancel — both land on Post-Run.

## Open questions

- Sequencing with [011](011-create-pre-run-screen.md): this item's
  Pre-Run button needs a screen to point to. Either this item ships
  alongside a minimal placeholder Pre-Run frame (with 011 filling in
  its real content later), or it's built right after 011 instead of
  strictly before it, despite the originally stated order.
- Final icon choices, once implemented and visible on screen.

## Status log

- 2026-07-23: Proposed as part of the original (too broad) item 009.
- 2026-07-23: Designed — split into a standalone item.
