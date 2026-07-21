# Contributing to Zarokh

Thanks for your interest in contributing! This document covers everything
you need to set up your environment, understand the project structure,
and submit changes.

## Requirements

- Python 3.11 or higher
- Windows 10/11 (the app relies on Windows-specific APIs: `winreg`, `ctypes`)
- [VSCode](https://code.visualstudio.com/) (recommended, not required)

## Setting up your environment

1. Clone the repository and open it in your favourite editor.
2. Create a virtual environment.
3. Install the dev dependencies:

```powershell
   pip install pytest
```

The project doesn't need to be installed as a package to run or test it —
`pyproject.toml` adds `src/` to the Python path automatically for both
`pytest` and normal execution.

## Running the app locally

```powershell
python -m zarokh
```

(Requires a `.env` file in the project root with `PYTHONPATH=src`, or an
equivalent setup in your editor/IDE of choice — see below.)

### Running/debugging in VSCode

Create a `.env` file in the project root:

```
PYTHONPATH=src
```

VSCode's Python extension picks this up automatically for both the Run
button and the debugger, resolving `from zarokh.timer import ...` without
installing the package. With this in place, you can also open
`src/zarokh/__main__.py` and press F5 directly.

## Running tests

```powershell
pytest
```

Tests live in `tests/`, one file per module (`test_timer.py`,
`test_config.py`, etc.), using pytest's `tmp_path` fixture to avoid
touching real files, and `unittest.mock` to isolate calls to the Windows
registry (`winreg`) and other OS-level APIs.

The CI pipeline runs the full suite on every tagged push before
compiling — see [Releasing](#releasing) below.

## Building the executable locally

To test a PyInstaller build without publishing a release:

```powershell
pip install pyinstaller
pyinstaller --noconsole --onefile --name "zarokh" --icon "assets/images/zarokh.ico" --paths src --add-data "assets;assets" src/zarokh/__main__.py
```

The executable will be at `dist/zarokh.exe`. `build/` and `dist/` are
gitignored — no need to clean them up manually.

## Logging

The app writes `zarokh.log` next to the executable (or in the project
root during development), rotating daily and keeping the previous day's
log. If you're debugging an issue, check this file first — most errors
are logged with context instead of failing silently.

## Implementing a roadmap item

When you finish implementing a roadmap item, update documentation as
part of the same change — not as an afterthought:

1. Update the item's detail doc under `docs/roadmap/`: set `Status`
   to `Done` and add a line to its `Status log`, noting anything that
   ended up different from the original design.
2. Update `ROADMAP.md`: mark the item's status in the table.
3. Update `README.md` if the change affects user-facing behavior
   (new/changed buttons, new files the app creates, changed
   requirements, etc.) — it should always describe the app as it
   currently behaves, not as it behaved before the change.
4. Add an entry to `CHANGELOG.md` under `## [Unreleased]` (see
   [Releasing](#releasing) below).

## Releasing

Before tagging a release, add an entry to `CHANGELOG.md` under a new
`## [X.Y.Z]` heading, following [Keep a Changelog](https://keepachangelog.com/)
conventions. The CI pipeline verifies this entry exists and fails fast
if it's missing.

Version numbers follow [semantic versioning](https://semver.org/):
bump the minor version for new features, the patch version for
bug fixes only, and the major version for breaking changes.

Releases are triggered by pushing a tag matching `v*` (e.g. `v1.2.0`),
following [semantic versioning](https://semver.org/). The version number
is derived automatically from the git tag via `setuptools_scm` — there's
no need to edit `pyproject.toml` manually. Pushing such a tag runs the
GitHub Actions workflow (`.github/workflows/build.yml`), which:

1. Verifies a matching CHANGELOG.md entry exists.
2. Runs the full test suite — the build is blocked if any test fails.
3. Compiles `zarokh.exe` with PyInstaller.
4. Runs a smoke test to confirm the executable starts correctly.
5. Publishes a GitHub Release with the executable attached.

```powershell
git tag v1.2.0
git push --tags
```

GitHub automatically computes and displays a SHA256 checksum for the
published `.exe`, so there's no need to generate one manually.

## Code style

- Code, comments, and commit messages are written in English.
- Type hints are expected on new functions and methods.
- Keep exceptions narrow (`except (OSError, json.JSONDecodeError)`, not
  bare `except:`), and log unexpected failures instead of silently
  swallowing them.
