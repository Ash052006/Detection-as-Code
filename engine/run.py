"""
Run every rule against every log entry and collect all the alerts.
"""

from typing import Any

from engine.match import matches


def run(rules: list[dict[str, Any]], logs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    alerts: list[dict[str, Any]] = []

    for rule in rules:
        # Skip rules that are turned off
        if not rule.get("enabled", True):
            continue

        for log in logs:
            # Does this rule say "match" for this log line?
            if matches(rule, log):
                # Yep — record which rule fired, how serious it is, and the log line
                alerts.append({
                    "rule_id": rule.get("id", "unknown"),
                    "severity": rule.get("severity", "medium"),
                    "log": log,
                })

    return alerts
