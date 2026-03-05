"""
Load log entries from a JSON file.
The engine uses this to read our "diary" (logs) from disk.
"""

# json.load() turns a JSON file into Python dicts/lists.
import json

# Path gives us a single way to work with file paths on any OS.
from pathlib import Path

# Any means "value can be anything" in type hints (e.g. dict values).
from typing import Any


def load_logs(logs_path: str | Path) -> list[dict[str, Any]]:
    """
    Load log entries from a JSON file.
    Accepts: a JSON array of log objects, or an object with 'logs' or 'entries' key.
    Returns a list of log dicts (one dict per event).
    """
    # Convert to Path so we can use .is_file() and pass it to open().
    path = Path(logs_path)

    # If the path doesn't exist or isn't a file, fail fast with a clear error.
    if not path.is_file():
        raise FileNotFoundError(f"Logs path not found: {logs_path}")

    # Open the file, read it, and parse the JSON into a Python object.
    # encoding="utf-8" handles any characters in the log text.
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    # JSON can be either:
    # 1. A top-level array: [ { log1 }, { log2 }, ... ] → we return it as-is.
    if isinstance(data, list):
        return data

    # 2. An object with a "logs" or "entries" key: { "logs": [ ... ] } → we return that array.
    if isinstance(data, dict):
        return data.get("logs", data.get("entries", []))

    # If it's neither (e.g. a string or number), we have no list to return.
    return []
