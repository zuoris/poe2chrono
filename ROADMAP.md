# Roadmap

This roadmap tracks planned features for Zarokh. Each item links to a
detail document under `docs/roadmap/` covering the problem, proposed
design, and open questions. Items are refined collaboratively before
implementation starts, one at a time, in priority order.

## Status legend
- **Proposed** — idea captured, design not yet refined
- **Designed** — design agreed, ready to implement
- **In Progress** — actively being implemented
- **Done** — shipped in a release

## Priority order

Simplifying the UI first frees up space for a better time display.
With more room, the detailed time/delta view becomes worthwhile. Full
run history then makes the attempt counter trivial to derive (it's
just a count of history entries). Relic tracking is last because it
requires the most UI work and depends on run history existing first.
Abandoned/interrupted run handling is unscheduled for now — it needs
further thought and isn't blocking the items above.

| Priority | # | Feature | Status |
|----------|---|---------|--------|
| 1 | 002 | [Simplified auto-mode UI](docs/roadmap/002-simplified-auto-mode-ui.md) | Done |
| 2 | 003 | [Detailed time and delta display](docs/roadmap/003-detailed-time-display.md) | Proposed |
| 3 | 004 | [Full run history](docs/roadmap/004-full-run-history.md) | Proposed |
| 4 | 001 | [Run attempt counter](docs/roadmap/001-run-attempt-counter.md) | Proposed |
| 5 | 005 | [Unique relic tracking per run](docs/roadmap/005-unique-relic-tracking.md) | Proposed |
| — | 006 | [Abandoned and interrupted runs](docs/roadmap/006-abandoned-interrupted-runs.md) | Proposed |
