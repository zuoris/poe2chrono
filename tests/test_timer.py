import pytest
from zarokh.timer import RunTimer, TOTAL_FLOORS


def test_register_floor_calculates_time_correctly():
    timer = RunTimer()
    timer.start()
    timer.accumulated_time = 10.0  # simulate 10s already elapsed
    timer.running = False
    timer.start()  # resume from 10.0

    result = timer.register_floor(best_time_for_floor=None)

    assert result.floor_number == 1
    assert result.is_new_record is True
    assert timer.current_floor == 2


def test_finished_run_is_marked_as_finished():
    timer = RunTimer(current_floor=5)
    assert timer.is_finished is True


def test_elapsed_time_stays_fixed_after_run_finishes():
    timer = RunTimer()
    timer.start()

    for _ in range(TOTAL_FLOORS - 1):
        timer.register_floor(best_time_for_floor=None)

    result = timer.register_floor(best_time_for_floor=None)

    assert timer.is_finished is True
    assert timer.running is False
    assert timer.elapsed_time() == pytest.approx(result.cumulative_time, abs=0.05)
