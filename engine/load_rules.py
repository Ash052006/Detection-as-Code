"""
Load detection rules from YAML file(s).
The engine uses this to read our "list of bad words" (rules) from disk.
"""

# Path handles both Windows and Unix paths, and lets us check "is it a file or folder?"
from pathlib import Path

# Type hints: we say "this function takes str or Path, returns list of dicts"
# so readers and tools know the contract without reading the body.
from typing import Any

# PyYAML turns YAML text into Python dicts/lists so we can work with rules in code.
import yaml


def load_rules(rules_path: str | Path) -> list[dict[str, Any]]:
    """
    Load rules from a single YAML file or a directory of .yaml files.
    Returns a list of rule dicts (each with id, condition, severity, etc.).
    """
    # Convert to Path so we can use .is_file(), .is_dir(), .glob() regardless of
    # whether the caller passed "rules" or Path("rules").
    path = Path(rules_path)

    # We'll append each loaded rule here and return this list at the end.
    rules: list[dict[str, Any]] = []

    # Branch 1: they gave us a single file (e.g. rules/suspicious-command.yaml).
    if path.is_file():
        # Open the file in read mode with UTF-8 so we handle any language in comments/text.
        with open(path, encoding="utf-8") as f:
            # safe_load reads one YAML document and returns a dict (our one rule).
            # We wrap it in a list so the return type is always "list of rules."
            rules.append(yaml.safe_load(f))

    # Branch 2: they gave us a folder (e.g. rules/) so we load every .yaml inside.
    elif path.is_dir():
        # glob("*.yaml") finds all files whose name ends with .yaml in that folder.
        # sorted() gives a stable order (e.g. alphabetical) so runs are predictable.
        for f in sorted(path.glob("*.yaml")):
            # Open this YAML file.
            with open(f, encoding="utf-8") as fp:
                # Parse it into a dict and add that dict as one rule to our list.
                rules.append(yaml.safe_load(fp))

    # If path doesn't exist or is something else (e.g. a broken symlink), we fail clearly.
    else:
        raise FileNotFoundError(f"Rules path not found: {rules_path}")

    # Return the list of rule dicts. Each dict has keys like id, condition, enabled, etc.
    return rules
