"""
Load log entries from a JSON file.
"""

import json
from pathlib import Path
from typing import Any


def load_logs(logs_path: str | Path) -> list[dict[str, Any]]:
    path = Path(logs_path)

    if not path.is_file():
        raise FileNotFoundError(f"Logs path not found: {logs_path}")

    # Read the file and turn the JSON into a Python list or dict
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    # If the JSON is already a list of log entries, we're done
    if isinstance(data, list):
        return data

    # Sometimes the file is like { "logs": [ ... ] } or { "entries": [ ... ] } — grab that inner list
    if isinstance(data, dict):
        return data.get("logs", data.get("entries", []))

    return []
