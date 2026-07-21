"""
Canonical list of Sekhemas' unique relics: full name (used as the
storage key and shown as a tooltip) and a short label for the run
history table column headers.
"""

RELICS = [
    ("The Last Flame", "Flame"),
    ("The Desperate Alliance", "Alliance"),
    ("The Burden of Leathership", "Burden"),
    ("The Changing Seasons", "Seasons"),
    ("The Peacemaker's Draught", "Draught"),
]

RELIC_NAMES = [name for name, _ in RELICS]


def default_relic_counts() -> dict[str, int]:
    return {name: 0 for name in RELIC_NAMES}
