# Zarokh: The Sekhemas Speedrun Tracker

This tool is called Zarokh in honor to the boss you are killing again and again :)

Zarokh tracks your Sekhemas run times automatically as you play, keeps
your personal bests, and logs the full history of every run —
completed or abandoned — including which unique relics dropped.

| Operating System | Compatibility |
|------------------|---------------|
| Windows 10 | YES |
| Windows 11 | YES |
| Linux | No |
| MacOS | No |

## Installing

Just download the latest release of `zarokh.exe` from the
[Releases page](https://github.com/zuoris/poe2chrono/releases).

## Running

Double click `zarokh.exe`.

Zarokh will try to locate your `Client.txt` file (PoE2's log file)
automatically. If it can't find it, it will ask you to locate it
yourself — this is required, the app keeps asking until you provide
a valid path.

This creates a few files next to the executable:
- `zarokh_data.json` — your best times and full run history.
- `zarokh_config.json` — your saved configuration.
- `zarokh.log` — diagnostic information, useful if you run into an
  issue and want to report it.

## Using Zarokh

The run is tracked automatically as you play. A small floating
window shows your global and per-floor clocks with live deltas
against your records, plus Pause/Restart and Cancel controls. A
hidden panel gives you access to your best times and the full run
history, where you can also log which unique relics dropped.

**For the full walkthrough of every screen, button, and behavior,
see the [User Guide](docs/USER_GUIDE.md).**

## Project status

- [CHANGELOG.md](CHANGELOG.md) — what's shipped in each release.
- [ROADMAP.md](ROADMAP.md) — what's planned next.

## Contributing

Interested in contributing to Zarokh? Check out
[CONTRIBUTING.md](CONTRIBUTING.md) for setup instructions, project
structure, and how to run tests.
