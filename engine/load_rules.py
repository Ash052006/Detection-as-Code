"""
Load detection rules from YAML file(s).
"""

from pathlib import Path
from typing import Any

import yaml


def load_rules(rules_path: str | Path) -> list[dict[str, Any]]:
    # Turn whatever they passed into a Path so we can check if it's a file or folder
    path = Path(rules_path)

    rules: list[dict[str, Any]] = []

    # Single file: open it, parse the YAML, add that one rule to the list
    if path.is_file():
        with open(path, encoding="utf-8") as f:
            rules.append(yaml.safe_load(f))

    # Folder: find every .yaml file in it, load each one, add to the list (sorted so order is stable)
    elif path.is_dir():
        for f in sorted(path.glob("*.yaml")):
            with open(f, encoding="utf-8") as fp:
                rules.append(yaml.safe_load(fp))

    # Path doesn't exist or isn't a file/folder — bail with a clear error
    else:
        raise FileNotFoundError(f"Rules path not found: {rules_path}")

    return rules
