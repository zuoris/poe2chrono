from zarokh.records import RecordsManager


def test_load_returns_defaults_when_file_does_not_exist(tmp_path):
    records = RecordsManager(data_path=tmp_path / "does_not_exist.json")
    assert records.best_floor_time(1) is None
    assert records.best_total_time() is None


def test_update_floor_time_sets_record_when_none_exists(tmp_path):
    records = RecordsManager(data_path=tmp_path / "records.json")

    is_new_record = records.update_floor_time(1, 45.5)

    assert is_new_record is True
    assert records.best_floor_time(1) == 45.5


def test_update_floor_time_replaces_record_when_better(tmp_path):
    records = RecordsManager(data_path=tmp_path / "records.json")
    records.update_floor_time(1, 45.5)

    is_new_record = records.update_floor_time(1, 40.0)

    assert is_new_record is True
    assert records.best_floor_time(1) == 40.0


def test_update_floor_time_keeps_record_when_worse(tmp_path):
    records = RecordsManager(data_path=tmp_path / "records.json")
    records.update_floor_time(1, 40.0)

    is_new_record = records.update_floor_time(1, 45.5)

    assert is_new_record is False
    assert records.best_floor_time(1) == 40.0


def test_update_total_time_sets_record_when_none_exists(tmp_path):
    records = RecordsManager(data_path=tmp_path / "records.json")

    is_new_record = records.update_total_time(180.0)

    assert is_new_record is True
    assert records.best_total_time() == 180.0


def test_clear_resets_all_records(tmp_path):
    records = RecordsManager(data_path=tmp_path / "records.json")
    records.update_floor_time(1, 40.0)
    records.update_total_time(180.0)

    records.clear()

    assert records.best_floor_time(1) is None
    assert records.best_total_time() is None


def test_records_persist_across_instances(tmp_path):
    data_path = tmp_path / "records.json"

    first_instance = RecordsManager(data_path=data_path)
    first_instance.update_floor_time(2, 30.0)

    second_instance = RecordsManager(data_path=data_path)

    assert second_instance.best_floor_time(2) == 30.0


def test_load_recovers_from_corrupted_file(tmp_path):
    data_path = tmp_path / "records.json"
    data_path.write_text("{ not valid json", encoding="utf-8")

    records = RecordsManager(data_path=data_path)

    assert records.best_floor_time(1) is None

def test_add_run_assigns_sequential_attempt_numbers(tmp_path):
    records = RecordsManager(data_path=tmp_path / "data.json")
    records.add_run([10.0, 12.0], 22.0)
    attempt = records.add_run([9.0], None)
    assert attempt == 2


def test_list_runs_returns_most_recent_first(tmp_path):
    records = RecordsManager(data_path=tmp_path / "data.json")
    records.add_run([10.0], None)
    records.add_run([9.0], None)
    runs = records.list_runs()
    assert runs[0]["attempt"] == 2
    assert runs[1]["attempt"] == 1


def test_cancelled_run_has_null_total_time(tmp_path):
    records = RecordsManager(data_path=tmp_path / "data.json")
    records.add_run([10.0, 12.0], None)
    assert records.list_runs()[0]["total_time"] is None


def test_migrates_legacy_records_file(tmp_path):
    legacy_path = tmp_path / "zarokh_records.json"
    legacy_path.write_text(
        '{"floors": [40.0, null, null, null], "total": null}', encoding="utf-8",
    )
    records = RecordsManager(data_path=tmp_path / "zarokh_data.json")
    assert records.best_floor_time(1) == 40.0
    assert records.list_runs() == []
