# Changelog

All notable changes to Zarokh will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

Versions prior to 1.0.14 were not documented in this file.

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