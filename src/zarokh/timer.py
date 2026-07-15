"""
Pure timer logic for a Sanctum run, with no UI dependencies.
"""
import time
from dataclasses import dataclass, field


TOTAL_FLOORS = 4


@dataclass
class FloorResult:
    """Result of completing a floor."""
    floor_number: int
    floor_time: float          # time it took to clear THIS floor
    cumulative_time: float     # total elapsed time up to this floor
    is_new_record: bool


@dataclass
class RunTimer:
    """
    Timer for a single Sanctum run. Knows nothing about Tkinter:
    it only holds state and does calculations. The UI just reads
    its properties and renders whatever this object gives it.
    """
    running: bool = False
    _start_time: float = 0.0
    accumulated_time: float = 0.0
    current_floor: int = 1
    floor_split_times: list = field(default_factory=list)

    def start(self) -> None:
        """Starts or resumes the timer."""
        if self.running:
            return
        self._start_time = time.time()
        self.running = True

    def pause(self) -> None:
        """Pauses the timer, accumulating the elapsed time."""
        if not self.running:
            return
        self.accumulated_time += time.time() - self._start_time
        self.running = False

    def toggle(self) -> None:
        """Toggles between start and pause."""
        self.pause() if self.running else self.start()

    def reset(self) -> None:
        """Resets the run to its initial state."""
        self.running = False
        self.accumulated_time = 0.0
        self.current_floor = 1
        self.floor_split_times = []

    @property
    def is_finished(self) -> bool:
        return self.current_floor > TOTAL_FLOORS

    def elapsed_time(self) -> float:
        """Total elapsed time for the run, in seconds."""
        if self.running:
            return self.accumulated_time + (time.time() - self._start_time)
        return self.accumulated_time

    def register_floor(self, best_time_for_floor: float | None) -> FloorResult | None:
        """
        Registers completion of the current floor.

        `best_time_for_floor` is the previous record for THIS floor
        (or None if there's no record yet) — passed in by whoever is
        orchestrating (records.py), so RunTimer doesn't need to know
        anything about persistence.

        Returns None if the floor can't be registered (timer stopped
        or run already finished).
        """
        if not self.running or self.is_finished:
            return None

        current_time = self.elapsed_time()
        self.floor_split_times.append(current_time)

        previous_time = (
            self.floor_split_times[self.current_floor - 2]
            if self.current_floor > 1
            else 0.0
        )
        floor_time = current_time - previous_time
        is_new_record = best_time_for_floor is None or floor_time < best_time_for_floor

        result = FloorResult(
            floor_number=self.current_floor,
            floor_time=floor_time,
            cumulative_time=current_time,
            is_new_record=is_new_record,
        )

        self.current_floor += 1
        if self.is_finished:
            self.pause()

        return result

    def current_delta(self, best_time_for_floor: float | None) -> float | None:
        """
        Live difference from the current floor's record.
        Negative = ahead of the record. None if there's no record yet.
        """
        if best_time_for_floor is None or self.is_finished:
            return None

        previous_time = (
            self.floor_split_times[self.current_floor - 2]
            if self.current_floor > 1
            else 0.0
        )
        partial_time = self.elapsed_time() - previous_time
        return partial_time - best_time_for_floor