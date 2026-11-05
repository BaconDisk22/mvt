"""Read-only SHA-256 verification for individual local evidence files."""
import hashlib
from pathlib import Path


def sha256_file(path, chunk_size=1024 * 1024):
    """Hash a regular file without modifying it or reading it all into memory."""
    path = Path(path)
    if not path.is_file() or path.is_symlink():
        raise ValueError("Expected a regular, non-symlink evidence file")
    if chunk_size < 1:
        raise ValueError("chunk_size must be positive")
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_sha256(path, expected):
    if len(expected) != 64 or any(c not in "0123456789abcdefABCDEF" for c in expected):
        raise ValueError("Expected a 64-character SHA-256 hexadecimal digest")
    return sha256_file(path) == expected.lower()



def sha256_manifest(paths):
    """Build a deterministic in-memory hash inventory, without writing evidence."""
    from pathlib import Path
    result = []
    seen = set()
    for item in paths:
        path = Path(item)
        resolved = str(path.absolute())
        if resolved in seen:
            raise ValueError("Duplicate evidence path")
        seen.add(resolved)
        digest = sha256_file(path)
        result.append({"file": path.name, "sha256": digest, "size_bytes": path.stat().st_size})
    return sorted(result, key=lambda record: (record["file"], record["sha256"]))
