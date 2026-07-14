# 001: Run attempt counter

**Status:** Proposed

## Problem

The app currently tracks best times per floor and per run, but doesn't
keep count of how many times the user has completed a run (killed
Zarokh). Users have no way to see how many attempts they've made.

## Proposed design

_To be refined._

## Open questions

- Does "attempt" mean every run started, or only runs completed
  (Zarokh killed)?
- Where should the counter live: `zarokh_records.json`, or a separate
  file?
- Where should it be displayed in the UI?

## Status log

- 2026-07-14: Proposed.