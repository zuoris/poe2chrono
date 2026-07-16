import pytest

from zarokh.run import Run, RunState, TOTAL_FLOORS


def test_starts_idle():
    run = Run()
    assert run.state == RunState.IDLE
    assert run.current_floor == 1


def test_start_transitions_to_running():
    run = Run()
    run.start()
    assert run.state == RunState.RUNNING
    assert run.total_timer.running is True
    assert run.floor_timer.running is True


def test_start_replaces_timers_with_fresh_instances():
    run = Run()
    run.start()
    old_total_timer = run.total_timer
    run.cancel()
    run.start()
    assert run.total_timer is not old_total_timer
    assert run.total_timer.elapsed_time() == pytest.approx(0.0, abs=0.05)


def test_start_is_idempotent_while_already_running():
    run = Run()
    run.start()
    timer_before = run.total_timer
    run.start()  # should be a no-op
    assert run.total_timer is timer_before


def test_toggle_pause_stops_and_resumes_without_changing_state():
    run = Run()
    run.start()

    run.toggle_pause()
    assert run.state == RunState.RUNNING
    assert run.is_paused is True

    run.toggle_pause()
    assert run.state == RunState.RUNNING
    assert run.is_paused is False


def test_cancel_stops_timers_without_zeroing_them(tmp_path=None):
    run = Run()
    run.start()
    run.total_timer.accumulated_time = 12.3  # simulate elapsed time
    run.cancel()

    assert run.state == RunState.IDLE
    assert run.total_timer.running is False
    assert run.total_timer.elapsed_time() == pytest.approx(12.3, abs=0.05)


def test_cancel_is_a_no_op_when_idle():
    run = Run()
    run.cancel()
    assert run.state == RunState.IDLE


def test_register_floor_returns_none_when_idle():
    run = Run()
    assert run.register_floor(best_time_for_floor=None) is None


def test_register_floor_returns_none_when_paused():
    run = Run()
    run.start()
    run.toggle_pause()
    assert run.register_floor(best_time_for_floor=None) is None


def test_register_floor_advances_floor_and_resets_floor_timer():
    run = Run()
    run.start()
    result = run.register_floor(best_time_for_floor=None)

    assert result.floor_number == 1
    assert run.current_floor == 2
    assert run.floor_timer.elapsed_time() == pytest.approx(0.0, abs=0.05)
    assert run.state == RunState.RUNNING


def test_finishing_the_run_pauses_timers_and_returns_to_idle():
    run = Run()
    run.start()
    for _ in range(TOTAL_FLOORS):
        result = run.register_floor(best_time_for_floor=None)

    assert run.state == RunState.IDLE
    assert run.current_floor == TOTAL_FLOORS + 1
    assert run.total_timer.running is False
    assert run.total_timer.elapsed_time() == pytest.approx(result.cumulative_time, abs=0.05)
