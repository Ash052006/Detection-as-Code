"""
CLI: run detection rules on logs and print alerts.
Simple: You tell us where the rules are and where the diary is. We read both, find bad words, and print every "bell!"
"""

import argparse

# We need these to: load rules, load logs, and run them together to get alerts.
from engine import load_logs, load_rules, run


def main() -> None:
    # argparse reads what you type after "python main.py" (e.g. --rules rules --logs logs/sample.json).
    parser = argparse.ArgumentParser(description="Run detection rules on logs and raise alerts.")
    parser.add_argument("--rules", required=True, help="Path to rules file or folder (e.g. rules or rules/suspicious-command.yaml)")
    parser.add_argument("--logs", required=True, help="Path to JSON log file (e.g. logs/sample.json)")
    args = parser.parse_args()

    # Step 1: Load the list of bad words (rules) from the path they gave.
    rules = load_rules(args.rules)

    # Step 2: Load the diary (logs) from the file they gave.
    logs = load_logs(args.logs)

    # Step 3: Run every rule on every log and get back the list of "bell!" moments.
    alerts = run(rules, logs)

    # Step 4: Print each alert in a structured block.
    sep = "-" * 60
    for i, a in enumerate(alerts, 1):
        log = a["log"]
        print(f"\n{sep}")
        print(f"  ALERT #{i}")
        print(f"  {sep[:56]}")
        print(f"  Rule ID   : {a['rule_id']}")
        print(f"  Severity  : {a['severity']}")
        print(f"  Timestamp : {log.get('timestamp', '-')}")
        print(f"  Source    : {log.get('source', '-')}")
        print(f"  Message   : {log.get('message', '-')}")
    print(f"\n{sep}")
    # Step 5: Print summary.
    print(f"  Total alerts: {len(alerts)}")
    print(f"{sep}\n")


if __name__ == "__main__":
    main()
