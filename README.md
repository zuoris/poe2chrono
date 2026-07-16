# Zarokh: The Sekhemas Speedrun Tracker

This tool is called Zarokh in honor to the boss you are killing again and again :)

So Zarokh allows you to track the time you last to kill Zarokh.

| Operating System | Compatibility |
|------------------|---------------|
| Windows 10 | YES |
| Windows 11 | YES |
| Linux | No |
| MacOS | No |

## Installing

Just download the last release of zarokh.exe file from the repository.

## Running

Doble click on zarokh.exe.

Zarokh will try to locate your "Client.txt" file (PoE2's log file)
automatically. If it can't find it, it will ask you to locate it
yourself — this is required, the app keeps asking until you provide
a valid path.

This will create some files in the same place where the executable is located:
- "zarokh_records.json" to store your record. When start the first Sekhemas run.
- "zarokh_config.json" to store your configuration. When executable starts at the first time.
- "zarokh.log" with diagnostic information about the app's execution. Useful if you run into an issue and want to report it.


## Using

This tool is extremly simple.

You can move the window wherever you want to see the clock.

The run is tracked automatically as you play — the app watches your
"Client.txt" file and reacts to it.

There are two small buttons to control the current run:
- **Pause/Restart** (⏸/▶): pauses the clock, or resumes it from where
  it left off. Hover over it to see which action it will perform.
- **Cancel** (✕): abandons the current run — the clock stops and no
  record is saved for it. Hover over it for confirmation.

Both buttons are disabled until you actually start a run (enter the
first floor of Sekhemas).

If you pause the clock and then clear a floor without resuming first,
the app assumes you forgot to hit Restart — the run is discarded
automatically, the same as clicking Cancel.

There is a hidden panel you can display on clicking "+" button.
This panel has information about your records and also you can reset your records clicking on "Clear records" button (WARNING! you will remove the information from the "zarokh_records.json" file).


## Contributing

Interested in contributing to Zarokh? Check out [CONTRIBUTING.md](CONTRIBUTING.md) for setup instructions, project structure, and how to run tests.
