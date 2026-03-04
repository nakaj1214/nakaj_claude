"""Atomic JSONL append and safe read with corrupt line isolation."""

import fcntl
import json
import os
from pathlib import Path


def append_jsonl(filepath: str, json_line: str) -> None:
    """Append a single JSON line to a JSONL file with exclusive file lock.

    Uses fcntl.flock(LOCK_EX) to prevent concurrent write corruption.
    Ensures data is flushed and synced to disk before releasing the lock.

    Parameters
    ----------
    filepath : str
        Path to the JSONL file. Parent directories are created if needed.
    json_line : str
        A single JSON string to append (newline is added automatically).
    """
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)

    fd = os.open(str(path), os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        line = json_line.rstrip("\n") + "\n"
        os.write(fd, line.encode("utf-8"))
        os.fsync(fd)
    finally:
        fcntl.flock(fd, fcntl.LOCK_UN)
        os.close(fd)


def read_jsonl_safe(filepath: str) -> list[dict]:
    """Read a JSONL file, isolating corrupt lines to a .corrupt file.

    Valid JSON lines are returned as a list of dicts.
    Corrupt lines (including empty lines) are written to {filepath}.corrupt.

    Parameters
    ----------
    filepath : str
        Path to the JSONL file to read.

    Returns
    -------
    list[dict]
        List of parsed JSON objects from valid lines.
    """
    path = Path(filepath)
    if not path.is_file():
        return []

    entries: list[dict] = []
    corrupt_lines: list[str] = []

    with open(path, encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            if not stripped:
                continue
            try:
                obj = json.loads(stripped)
                entries.append(obj)
            except (json.JSONDecodeError, ValueError):
                corrupt_lines.append(line)

    if corrupt_lines:
        corrupt_path = str(filepath) + ".corrupt"
        with open(corrupt_path, "a", encoding="utf-8") as cf:
            for cl in corrupt_lines:
                cf.write(cl if cl.endswith("\n") else cl + "\n")

    return entries
