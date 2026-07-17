# 003: Detailed time and delta display

**Status:** Proposed

## Problem

The current display only shows the current elapsed time and a delta
against the floor record. It doesn't show:
- Total run time and its delta against the total time record.
- The current floor's elapsed time (isolated from the run's total
  elapsed time) and its delta against that floor's record.
# 003: Detailed time and delta display

**Status:** Designed

## Problem

The current display only shows the current elapsed time and a delta
against the floor record. It doesn't show:
- Total run time and its delta against the total time record.
- The current floor's elapsed time (isolated from the run's total
  elapsed time) and its delta against that floor's record.

## Proposed design

### What's shown

- **Global clock**: total elapsed time for the run (`total_timer`),
  in the same position it occupies today (top of the window).
- **Global delta**: difference in seconds against the best total
  time record, shown to the right of the global clock. Smaller font
  than the clock itself. Green if the current time is better than
  the record, red if worse.
- **Floor clock**: elapsed time for the current floor (`floor_timer`),
  in the position the delta label occupies today. Font size smaller
  than the global clock.
- **Floor delta**: difference in seconds against the best time
  record for the current floor, shown to the right of the floor
  clock. Same smaller font size as the global delta, same
  green/red rule.
- **Floor indicator**: minimal marker (`F1`, `F2`, `F3`, `F4`)
  showing which floor is currently being tracked, placed near the
  floor clock.

### Layout

Clock positions stay where they are today; deltas are added to the
right of each clock rather than introducing a separate row or panel:

```
[  00:42.17  ]  +2.3s      <- global clock + global delta
F2 [ 00:08.04 ]  -1.1s      <- floor indicator + floor clock + floor delta
```

The panel stays as compact as possible while keeping both clocks and
both deltas comfortably readable. The current window size is assumed
to be enough; if it turns out not to be during implementation, the
window can grow — to be judged once this is actually built and seen
on screen.

### Zero state

On app start (and, per item 002's design, until a run actually
starts), both clocks show `00:00.00`, consistent with the existing
"only zero at app start or when a new run begins" rule.

## Status log

- 2026-07-14: Proposed.
- 2026-07-14: Designed — layout, sizing, and color rules defined
  based on refined requirements; all prior open questions resolved.
