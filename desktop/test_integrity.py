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
