import pytest

from zarokh.app_controller import AppController
from zarokh.records import RecordsManager
from zarokh.run import Run, RunState


def make_controller(tmp_path):
    run = Run()
    records = RecordsManager(data_path=tmp_path / "records.json")
    return AppController(run=run, records=records), run, records


def test_start_event_starts_a_fresh_run(tmp_path):
    controller, run, _ = make_controller(tmp_path)
    controller.handle_log_event("START")
    assert run.state == RunState.RUNNING
    assert run.current_floor == 1


def test_start_event_ignored_when_already_running(tmp_path):
    controller, run, _ = make_controller(tmp_path)
    controller.handle_log_event("START")
    controller.handle_log_event("FLOOR_2")

    controller.handle_log_event("START")

    assert run.current_floor == 2  # untouched


def test_start_event_starts_fresh_after_previous_run_finished(tmp_path):
    controller, run, _ = make_controller(tmp_path)
    controller.handle_log_event("START")
    for event in ["FLOOR_2", "FLOOR_3", "FLOOR_4", "END"]:
        controller.handle_log_event(event)
    assert run.state == RunState.IDLE

    controller.handle_log_event("START")

    assert run.state == RunState.RUNNING
    assert run.current_floor == 1


def test_start_event_starts_fresh_after_cancel(tmp_path):
    controller, run, _ = make_controller(tmp_path)
    controller.handle_log_event("START")
    controller.handle_log_event("FLOOR_2")
    controller.cancel()

    controller.handle_log_event("START")

    assert run.state == RunState.RUNNING
    assert run.current_floor == 1


def test_floor_event_registers_floor_when_running(tmp_path):
    controller, run, records = make_controller(tmp_path)
    controller.handle_log_event("START")

    update = controller.handle_log_event("FLOOR_2")

    assert update is not None
    assert records.best_floor_time(1) is not None
    assert run.current_floor == 2


def test_floor_event_ignored_when_out_of_order(tmp_path):
    controller, run, _ = make_controller(tmp_path)
    controller.handle_log_event("START")

    update = controller.handle_log_event("FLOOR_3")

    assert update is None
    assert run.current_floor == 1


def test_floor_event_ignored_when_idle(tmp_path):
    controller, run, _ = make_controller(tmp_path)
    update = controller.handle_log_event("FLOOR_2")
    assert update is None


def test_end_event_finishes_run_and_saves_total_record(tmp_path):
    controller, run, records = make_controller(tmp_path)
    controller.handle_log_event("START")
    controller.handle_log_event("FLOOR_2")
    controller.handle_log_event("FLOOR_3")
    controller.handle_log_event("FLOOR_4")

    update = controller.handle_log_event("END")

    assert update.is_run_finished is True
    assert records.best_total_time() is not None
    assert run.state == RunState.IDLE


def test_floor_event_while_paused_cancels_run_without_saving(tmp_path):
    controller, run, records = make_controller(tmp_path)
    controller.handle_log_event("START")
    controller.toggle_pause()  # paused before completing floor 1

    update = controller.handle_log_event("FLOOR_2")

    assert update is None
    assert records.best_floor_time(1) is None
    assert run.state == RunState.IDLE


def test_cancel_discards_run_without_saving_records(tmp_path):
    controller, run, records = make_controller(tmp_path)
    controller.handle_log_event("START")
    controller.handle_log_event("FLOOR_2")  # floor 1 saved

    controller.cancel()

    assert run.state == RunState.IDLE
    assert records.best_floor_time(1) is not None  # already-saved floor stays
    assert records.best_total_time() is None  # total never got saved

def test_finishing_a_run_adds_it_to_history(tmp_path):
    controller, run, records = make_controller(tmp_path)
    controller.handle_log_event("START")
    for event in ["FLOOR_2", "FLOOR_3", "FLOOR_4", "END"]:
        controller.handle_log_event(event)

    runs = records.list_runs()
    assert len(runs) == 1
    assert runs[0]["total_time"] is not None
    assert len(runs[0]["floor_times"]) == 4


def test_cancelling_a_run_adds_it_to_history_with_null_total(tmp_path):
    controller, run, records = make_controller(tmp_path)
    controller.handle_log_event("START")
    controller.handle_log_event("FLOOR_2")
    controller.cancel()

    runs = records.list_runs()
    assert len(runs) == 1
    assert runs[0]["total_time"] is None
    assert runs[0]["floor_times"] == [pytest.approx(runs[0]["floor_times"][0], abs=0.05)]
