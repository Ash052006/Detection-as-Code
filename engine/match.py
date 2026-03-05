"""
Rule-vs-log matching logic.
Simple: We have one rule (bad words) and one diary line (log). Do we ring the bell? Yes or no.
"""

# We need "Any" so we can say "this box can hold anything" in type hints.
from typing import Any


def matches(rule: dict[str, Any], log: dict[str, Any]) -> bool:
    """
    One rule + one log → True (ring bell) or False (no bell).
    """
    # Open the rule and get the part that says "how to check" (the condition).
    # If the rule has no condition, use an empty box {} so we don't fall over.
    cond = rule.get("condition", {})

    # Our rule must say "log_match" (look for words in the diary line).
    # If it says something else, we don't know it yet → say "no bell."
    if cond.get("type") != "log_match":
        return False

    # Which part of the diary line do we look at? Usually "message" (the main sentence).
    field = cond.get("field", "message")

    # Get the list of bad words from the rule.
    patterns = cond.get("patterns", [])

    # Get that one part (e.g. the message) from the diary line.
    # If it's not there, use "" (empty sentence) so we don't fall over.
    value = log.get(field) or ""

    # Is any bad word inside this sentence? Yes → True (bell). No → False (no bell).
    return any(p in value for p in patterns)
