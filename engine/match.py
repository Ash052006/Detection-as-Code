"""
Check if one rule matches one log entry (do we ring the bell or not).
"""

from typing import Any


def matches(rule: dict[str, Any], log: dict[str, Any]) -> bool:
    # Get the "condition" part of the rule — that's where we learn how to check
    cond = rule.get("condition", {})

    # We only know how to do "log_match" (look for words in a field). Anything else = no match
    if cond.get("type") != "log_match":
        return False

    # Which field in the log do we look at? Usually "message"
    field = cond.get("field", "message")

    # The list of bad words / patterns from the rule
    patterns = cond.get("patterns", [])

    # Get that field from the log (e.g. the message text). Use empty string if it's missing
    value = log.get(field) or ""

    # If any of the patterns appear in that value, we have a match — ring the bell
    return any(p in value for p in patterns)
