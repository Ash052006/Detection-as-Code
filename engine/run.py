"""
Orchestrate rules + logs and produce alerts.
Simple: We have the whole list of bad words (rules) and the whole diary (logs).
We look at every diary line with every list of bad words. When we find a match → we write down "bell!" (alert).
"""

from typing import Any

# We need matches to ask "for this rule and this log, bell or no bell?"
from engine.match import matches


def run(rules: list[dict[str, Any]], logs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Run all rules over all log entries. Return a list of alerts.
    Each alert has: rule_id, severity, and the log that matched.
    """
    # We start with an empty list. Every time we ring the bell, we add one alert to this list.
    alerts: list[dict[str, Any]] = []

    # For each rule (each "list of bad words")...
    for rule in rules:
        # If the rule is turned off (enabled: false), skip it. No bell for this rule.
        if not rule.get("enabled", True):
            continue

        # For each line in the diary (each log entry)...
        for log in logs:
            # Does this rule say "bell" for this line? (matches = True or False)
            if matches(rule, log):
                # Yes! So we write down: which rule, how serious, and the diary line.
                alerts.append({
                    "rule_id": rule["id"],
                    "severity": rule.get("severity", "medium"),
                    "log": log,
                })

    # Give back the full list of "bell!" moments.
    return alerts