"""Evidence integrity utility tests."""
import hashlib
import importlib.util
from pathlib import Path
import pytest

spec = importlib.util.spec_from_file_location("desktop_integrity", Path(__file__).with_name("integrity.py"))
integrity = importlib.util.module_from_spec(spec)
spec.loader.exec_module(integrity)


def test_hash_matches_reference(tmp_path):
    file = tmp_path / "evidence.bin"
    file.write_bytes(b"forensic sample")
    expected = hashlib.sha256(b"forensic sample").hexdigest()
    assert integrity.sha256_file(file, chunk_size=3) == expected
    assert integrity.verify_sha256(file, expected.upper())
    assert not integrity.verify_sha256(file, "0" * 64)


def test_reject_symlinks(tmp_path):
    file = tmp_path / "real"
    file.write_bytes(b"data")
    link = tmp_path / "link"
    link.symlink_to(file)
    with pytest.raises(ValueError):
        integrity.sha256_file(link)


def test_reject_bad_digest(tmp_path):
    with pytest.raises(ValueError):
        integrity.verify_sha256(tmp_path / "none", "not-a-digest")



def test_manifest_is_deterministic_and_read_only(tmp_path):
    first = tmp_path / "a.bin"
    second = tmp_path / "b.bin"
    first.write_bytes(b"a")
    second.write_bytes(b"bb")
    result = integrity.sha256_manifest([second, first])
    assert [item["file"] for item in result] == ["a.bin", "b.bin"]
    assert [item["size_bytes"] for item in result] == [1, 2]
    assert len(result[0]["sha256"]) == 64
    assert len(list(tmp_path.iterdir())) == 2


def test_manifest_rejects_duplicates(tmp_path):
    path = tmp_path / "evidence"
    path.write_bytes(b"sample")
    with pytest.raises(ValueError):
        integrity.sha256_manifest([path, path])
