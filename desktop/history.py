"""Minimal local scan execution history; no evidence contents or paths stored."""
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


def history_root():
    return Path.home() / "Library" / "Application Support" / "MVT Forensic Suite" / "history"


def save_scan(status, case_id=None, root=None):
    if status not in {"completed", "failed", "timed_out"}:
        raise ValueError("Unsupported scan status")
    if case_id is not None and (len(case_id) != 32 or any(c not in "0123456789abcdef" for c in case_id)):
        raise ValueError("Invalid case identifier")
    directory = Path(root) if root is not None else history_root()
    directory.mkdir(mode=0o700, parents=True, exist_ok=True)
    record = {"id": uuid4().hex, "created_at": datetime.now(timezone.utc).isoformat(), "status": status, "case_id": case_id}
    fd = os.open(directory / (record["id"] + ".json"), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        json.dump(record, handle)
    return record


def list_scans(root=None):
    directory = Path(root) if root is not None else history_root()
    if not directory.exists():
        return []
    records = []
    for path in directory.glob("*.json"):
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(record, dict) and {"id", "created_at", "status"} <= record.keys():
                records.append(record)
        except (OSError, ValueError, UnicodeError):
            continue
    return sorted(records, key=lambda r: r["created_at"], reverse=True)
