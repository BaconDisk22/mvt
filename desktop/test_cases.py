"""Tests for local case metadata."""
import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location("mvt_desktop_cases", Path(__file__).with_name("cases.py"))
cases = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cases)


def test_case_creation_and_listing(tmp_path):
    record = cases.create_case("Test investigation", tmp_path)
    assert record["name"] == "Test investigation"
    assert cases.list_cases(tmp_path)[0]["id"] == record["id"]
    assert (tmp_path / (record["id"] + ".json")).stat().st_mode & 0o777 == 0o600


def test_case_rejects_empty_names(tmp_path):
    try:
        cases.create_case("   ", tmp_path)
    except ValueError:
        pass
    else:
        raise AssertionError("Empty case name accepted")


def test_case_list_skips_corrupt_metadata(tmp_path):
    (tmp_path / "broken.json").write_text("{not-json")
    assert cases.list_cases(tmp_path) == []
