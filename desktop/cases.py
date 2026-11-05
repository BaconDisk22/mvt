"""Local case metadata; never copies source evidence or scan contents."""
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


def case_root():
    """Private per-user application data directory."""
    return Path.home() / "Library" / "Application Support" / "MVT Forensic Suite" / "cases"


def create_case(label, root=None):
    """Create a case with minimal metadata; paths to evidence are not stored."""
    label = label.strip()
    if not label or len(label) > 120:
        raise ValueError("Case name must be 1–120 characters")
    directory = Path(root) if root is not None else case_root()
    directory.mkdir(mode=0o700, parents=True, exist_ok=True)
    case_id = uuid4().hex
    record = {
        "id": case_id,
        "name": label,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "new",
    }
    path = directory / (case_id + ".json")
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as stream:
        json.dump(record, stream, indent=2)
    return record


def list_cases(root=None):
    directory = Path(root) if root is not None else case_root()
    if not directory.exists():
        return []
    records = []
    for path in directory.glob("*.json"):
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(record, dict) and {"id", "name", "created_at"} <= record.keys():
                records.append(record)
        except (OSError, ValueError, UnicodeError):
            continue
    return sorted(records, key=lambda record: record["created_at"], reverse=True)
