"""Smoke tests for packaged GUI command routing."""
import importlib.util
from pathlib import Path
import sys
from unittest.mock import Mock

spec = importlib.util.spec_from_file_location("desktop_app", Path(__file__).with_name("app.py"))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_scan_command_keeps_paths_as_arguments():
    assert module.scan_command("/Applications/MVT.app/Contents/MacOS/MVT", "/tmp/a b", "/tmp/out") == [
        "/Applications/MVT.app/Contents/MacOS/MVT", "--mvt-scan-worker", "--output", "/tmp/out", "/tmp/a b"
    ]


def test_worker_routes_to_mvt_ios(monkeypatch):
    fake = Mock()
    monkeypatch.setitem(sys.modules, "mvt.ios", Mock(main=fake))
    monkeypatch.setattr(sys, "argv", ["app"])
    module.worker_main(["--output", "/tmp/out", "/tmp/backup"])
    fake.assert_called_once_with()
    assert sys.argv == ["mvt-ios", "check-backup", "--output", "/tmp/out", "/tmp/backup"]
