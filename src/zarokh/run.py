"""
Tracks the lifecycle of a single Sanctum run: its state and current
floor. Delegates all time measurement to two Stopwatch instances
(total and per-floor) — Run itself does no time math.
"""
from dataclasses import dataclass, field
from enum import Enum, auto

from zarokh.stopwatch import Stopwatch

TOTAL_FLOORS = 4


class RunState(Enum):
    IDLE = auto()
    RUNNING = auto()


@dataclass
class FloorResult:
    floor_number: int
    floor_time: float
    cumulative_time: float
    is_new_record: bool


@dataclass
class Run:
    state: RunState = RunState.IDLE
    current_floor: int = 1
    total_timer: Stopwatch = field(default_factory=Stopwatch)
    floor_timer: Stopwatch = field(default_factory=Stopwatch)

    @property
    def is_paused(self) -> bool:
        """True only while a run is in progress but its timers are
        stopped — not to be confused with IDLE, which means there's
        no run in progress at all."""
        return self.state == RunState.RUNNING and not self.total_timer.running

    def start(self) -> None:
        """Starts a brand new run. Only valid from IDLE — replaces
        both timers with fresh instances, so it never matters what
        the previous run's timers held (whether it ended via
        finishing or via cancel)."""
        if self.state == RunState.RUNNING:
            return
        self.current_floor = 1
        self.total_timer = Stopwatch()
        self.floor_timer = Stopwatch()
        self.total_timer.start()
        self.floor_timer.start()
        self.state = RunState.RUNNING

    def toggle_pause(self) -> None:
        """Pauses or resumes the current run in place. Does not
        change the run's state — it stays RUNNING throughout; only
        the underlying timers stop or resume counting."""
        if self.state != RunState.RUNNING:
            return
        self.total_timer.toggle()
        self.floor_timer.toggle()

    def cancel(self) -> None:
        """Abandons the current run: stops the timers (their values
        are left as-is, not zeroed — the next start() will replace
        them) and no record is ever saved for this run."""
        if self.state != RunState.RUNNING:
            return
        self.total_timer.pause()
        self.floor_timer.pause()
        self.state = RunState.IDLE

    def register_floor(self, best_time_for_floor: float | None) -> FloorResult | None:
        """
        Registers completion of the current floor. Returns None if
        there's no active, unpaused run to register against — the
        caller (AppController) decides what a paused run completing
        a floor means (treated as forgetting to resume, and
        cancelled).
        """
        if self.state != RunState.RUNNING or self.is_paused:
            return None
        if self.current_floor > TOTAL_FLOORS:
            return None

        floor_time = self.floor_timer.elapsed_time()
        cumulative_time = self.total_timer.elapsed_time()
        is_new_record = best_time_for_floor is None or floor_time < best_time_for_floor

        result = FloorResult(
            floor_number=self.current_floor,
            floor_time=floor_time,
            cumulative_time=cumulative_time,
            is_new_record=is_new_record,
        )

        self.current_floor += 1

        if self.current_floor > TOTAL_FLOORS:
            # Zarokh is dead — stop the clocks, but leave their final
            # values visible; only the next start() will zero them.
            self.total_timer.pause()
            self.floor_timer.pause()
            self.state = RunState.IDLE
        else:
            self.floor_timer.reset()
            self.floor_timer.start()

        return result
