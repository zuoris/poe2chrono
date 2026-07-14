from zarokh.records import RecordsManager


def test_load_returns_defaults_when_file_does_not_exist(tmp_path):
    records = RecordsManager(records_path=tmp_path / "does_not_exist.json")
    assert records.best_floor_time(1) is None
    assert records.best_total_time() is None


def test_update_floor_time_sets_record_when_none_exists(tmp_path):
    records = RecordsManager(records_path=tmp_path / "records.json")

    is_new_record = records.update_floor_time(1, 45.5)

    assert is_new_record is True
    assert records.best_floor_time(1) == 45.5


def test_update_floor_time_replaces_record_when_better(tmp_path):
    records = RecordsManager(records_path=tmp_path / "records.json")
    records.update_floor_time(1, 45.5)

    is_new_record = records.update_floor_time(1, 40.0)

    assert is_new_record is True
    assert records.best_floor_time(1) == 40.0


def test_update_floor_time_keeps_record_when_worse(tmp_path):
    records = RecordsManager(records_path=tmp_path / "records.json")
    records.update_floor_time(1, 40.0)

    is_new_record = records.update_floor_time(1, 45.5)

    assert is_new_record is False
    assert records.best_floor_time(1) == 40.0


def test_update_total_time_sets_record_when_none_exists(tmp_path):
    records = RecordsManager(records_path=tmp_path / "records.json")

    is_new_record = records.update_total_time(180.0)

    assert is_new_record is True
    assert records.best_total_time() == 180.0


def test_clear_resets_all_records(tmp_path):
    records = RecordsManager(records_path=tmp_path / "records.json")
    records.update_floor_time(1, 40.0)
    records.update_total_time(180.0)

    records.clear()

    assert records.best_floor_time(1) is None
    assert records.best_total_time() is None


def test_records_persist_across_instances(tmp_path):
    records_path = tmp_path / "records.json"

    first_instance = RecordsManager(records_path=records_path)
    first_instance.update_floor_time(2, 30.0)

    second_instance = RecordsManager(records_path=records_path)

    assert second_instance.best_floor_time(2) == 30.0


def test_load_recovers_from_corrupted_file(tmp_path):
    records_path = tmp_path / "records.json"
    records_path.write_text("{ not valid json", encoding="utf-8")

    records = RecordsManager(records_path=records_path)

    assert records.best_floor_time(1) is None