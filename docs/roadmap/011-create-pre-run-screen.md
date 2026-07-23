# 011: Create the Pre-Run screen

**Status:** Designed (MVP scope only — expected to grow over time)

## Problem

There's no screen to help the user get ready before starting a run.

## Proposed design

- Minimal first version: a **Ready** button. Pressing it switches
  the visible screen to Run. Ready does **not** itself start the
  clock — `Run.start()` remains driven by the game log's `START`
  trigger exactly as it works today; Ready is purely a screen
  transition, getting the user into position before the clock
  begins.
- This screen's content is expected to expand over future
  refinements (e.g. showing personal bests or relic totals as a
  quick reference, configuration options) — none of that is
  designed yet, intentionally kept out of this MVP.
- Reached via the nav menu's Pre-Run button
  ([010](010-navigation-menu.md)), and shown by default when the app
  launches.

## Open questions

- Confirm Pre-Run is the default screen shown on app launch.
- Confirm the MVP truly has nothing but the Ready button (plus the
  nav menu) — no other content — for this first version.

## Status log

- 2026-07-23: Proposed as part of the original (too broad) item 009.
- 2026-07-23: Designed (MVP scope) — split into a standalone item.
