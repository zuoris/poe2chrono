# Changelog

All notable changes to Zarokh will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

Versions prior to 1.0.14 were not documented in this file.

## [1.1.0] - 2026-07-14

### Added
- Unique relic tracking in the run history window: a totals row for
  all five relics, pinned above the best-times row, and per-run
  +/- editing for completed runs.

## [1.0.17] - 2026-07-14

### Added
- Full run history window: a pinned personal-best row plus a
  scrollable list of past runs (completed or cancelled), most recent
  first, with the attempt number as the first column.
- "View History" button in the hidden records panel.

### Changed
- Persistence file renamed from zarokh_records.json to
  zarokh_data.json to also store run history. Existing users' data
  is migrated automatically on first launch after updating.

### Fixed
- The end-of-run trigger only matched one specific line, which never
  actually appeared in the game's log — Zarokh, the Temporal has
  five different possible death lines, and finishing a run wasn't
  being reliably detected. All five are now matched.

## [1.0.16] - 2026-07-14

### Added
- Detailed time display: global clock with total-time delta, and a
  separate (smaller) floor clock with its own delta against the
  floor record. Deltas show in green/red depending on sign, or "--"
  when there's nothing to compare yet.
- Minimal "Floor N" indicator showing the currently tracked floor.
- Small clickable "by Zuo" credit link to the project repository.

### Fixed
- Close button could be visually covered by other widgets.
- The records panel window height was hand-tuned and drifted out of
  sync whenever its content changed, leaving a mismatched-color gap
  at the bottom. The window now sizes itself to its actual content.

## [1.0.15] - 2026-07-14

### Changed
- Simplified the UI to automatic-mode-only tracking: manual mode
  (Start/Floor/Reset) removed, replaced by Pause/Restart and Cancel
  icon buttons.
- A floor completed while the timer is paused now silently cancels
  the run instead of registering a stale record — the app assumes
  the user forgot to resume.

### Added
- Integration tests covering AppController scenarios and the
  Tkinter UI's real widget state.

## [1.0.14] - 2026-07-14

### Added
- Daily-rotating log file (`zarokh.log`), written next to the
  executable, to help diagnose issues.
- Smoke test in the release pipeline: the build fails if the
  compiled executable doesn't stay running.
- `CONTRIBUTING.md` with setup instructions, project structure, and
  the release process.
- Package version is now derived automatically from the git tag via
  `setuptools_scm`, instead of being kept in sync manually in
  `pyproject.toml`.

### Changed
- Internal refactor: business logic (timer, config, records, log
  watching, Windows taskbar/icon handling) split into independent,
  unit-tested modules, decoupled from the Tkinter UI.
- Test suite now gates release builds in CI — a failing test blocks
  the release.

### Fixed
- The application icon was missing from the compiled executable
  because the `assets/` folder wasn't bundled by PyInstaller.

## [1.0.13] and earlier

Undocumented. Refer to the git history for changes prior to this file
being introduced.
