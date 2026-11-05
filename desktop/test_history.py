"""Local scan metadata tests."""
import importlib.util
from pathlib import Path
import pytest

spec = importlib.util.spec_from_file_location("desktop_history", Path(__file__).with_name("history.py"))
history = importlib.util.module_from_spec(spec)
spec.loader.exec_module(history)


def test_history_records_minimal_metadata(tmp_path):
    record = history.save_scan("completed", root=tmp_path)
    assert history.list_scans(tmp_path) == [record]
    assert set(record) == {"id", "created_at", "status", "case_id"}
    assert (tmp_path / (record["id"] + ".json")).stat().st_mode & 0o777 == 0o600


def test_reject_invalid_status(tmp_path):
    with pytest.raises(ValueError):
        history.save_scan("running", root=tmp_path)


def test_reject_invalid_case_id(tmp_path):
    with pytest.raises(ValueError):
        history.save_scan("failed", case_id="../secret", root=tmp_path)
