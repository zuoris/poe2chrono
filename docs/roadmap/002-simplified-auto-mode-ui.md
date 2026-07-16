# 002: Simplified auto-mode UI

**Status:** Designed

## Problem

The app currently has both a manual mode (Start/Floor/Reset buttons,
used when `Client.txt` isn't found) and an automatic mode driven by
game log events. In practice, `Client.txt` always exists as long as
PoE2 is installed, and the app already has a mechanism to prompt the
user for its location if it isn't auto-detected. This means manual
mode is unnecessary complexity: the user is never actually blocked
from reaching automatic mode, so there's no real scenario where manual
tracking is needed.

## Proposed design

### Manual mode is removed entirely

- No manual mode, no manual/automatic mode toggle, and no UI text
  indicating which mode is active — there's only one mode now.
- The user must provide the `Client.txt` location (auto-detected or
  manually selected via the existing file picker) before the app can
  be used at all. If it can't be located, the app keeps prompting for
  it rather than falling back to a manual tracking mode.
- This removes the need for `auto_mode` state, the mode indicator
  button/label, and the manual/automatic branching logic in
  `CronometroOverlay` and `AppController`.

### Controls

Two small icon buttons, replacing Start/Floor/Reset entirely:

- **Pause / Restart** — a single toggle button.
  - Icon: pause symbol while the run is active.
  - Clicking it stops the timer and switches the icon to a play
    symbol, with the button now acting as **Restart**.
  - Clicking **Restart** resumes the timer from where it left off
    (no reset of elapsed time or current floor) and switches the icon
    back to pause.
- **Cancel** — a small button with an X icon.
  - Abandons the current run: stops the timer, resets elapsed time
    and floor progress to zero, and discards the run — **no record is
    saved**, for any floor or the total time.
  - Semantically, Cancel means "abandon this run"; zeroing the counter
    is just an implicit side effect of that, not its purpose. A
    separate, general-purpose "Reset" control doesn't make sense
    without manual mode, so it's removed as an independent button —
    Cancel is the only way to zero the counter now, and it always
    means abandoning the run.

Both buttons show their name (`Pause` / `Cancel`) as a tooltip on
hover, since only icons are displayed.

Both buttons are **disabled until the run actually starts** (i.e.
until the `START` log trigger is detected and the timer begins
running), to prevent pausing or cancelling a run that hasn't begun.

### Mapping to existing code

- Pause/Restart maps directly to the existing `AppController.toggle()`
  — no new controller logic needed, just new UI wiring and iconography.
- Cancel maps to `AppController.reset()` as-is — the existing method
  already does exactly what's needed (stop the timer, zero elapsed
  time and floor progress, without touching stored records). The UI
  just exposes it as "Cancel" instead of "Reset", since that's what it
  now means in a single-mode app.

### Implementation notes

- Tkinter has no built-in tooltip widget — a small custom tooltip
  helper (a `Toplevel` shown on `<Enter>` / hidden on `<Leave>`) will
  be needed for the hover text on both buttons.
- Removing manual mode means removing: `auto_mode` parameter,
  `on_manual_path_selected` callback and the file-picker wiring for
  switching modes at runtime, `btn_modo_status` and
  `_refresh_mode_indicator()`, and the Start/Floor/Reset buttons and
  their handlers in `CronometroOverlay`. The file picker itself is
  still needed for the initial "couldn't find Client.txt, please
  select it" flow — only the runtime mode-switching goes away.

## Out of scope

Handling runs that are abandoned or temporarily interrupted mid-way
through a Sekhemas attempt (the player can either leave for good or
resume later) is a more complex behavior that needs its own design.
It's tracked separately as
[006 (Abandoned and interrupted runs)](006-abandoned-interrupted-runs.md).
For now, floor times keep being recorded as each floor completes, same
as today — Cancel is a manual, explicit action by the user, not an
automatic detection of abandonment.

## Status log

- 2026-07-14: Proposed.
- 2026-07-14: Designed — Pause/Restart/Cancel button behavior defined.
- 2026-07-14: Refined — manual mode removed entirely; Cancel and Reset
  reconciled (Cancel is the only reset mechanism now); abandoned/
  interrupted runs split out into a new backlog item (006).
- 2026-07-14: Implemented. Final design ended up simpler than
  originally specified: only two Run states (IDLE, RUNNING); pause
  is a derived property, not a state. Manual mode fully removed.
