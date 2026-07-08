"""
Run detection rules on logs and print alerts. Optionally add AI explanations and a Q&A chat.
"""

import argparse
from pathlib import Path

from dotenv import load_dotenv

# Pull in HF_TOKEN from the .env file in this folder so we can use it later for AI
_load_env = Path(__file__).resolve().parent / ".env"
load_dotenv(_load_env, override=True)

from engine import load_logs, load_rules, run


def main() -> None:
    # Set up the command-line options so the user can pass --rules, --logs, etc.
    parser = argparse.ArgumentParser(description="Run detection rules on logs and raise alerts.")
    parser.add_argument("--rules", required=True, help="Path to rules file or folder (e.g. rules or rules/suspicious-command.yaml)")
    parser.add_argument("--logs", required=True, help="Path to JSON log file (e.g. logs/sample.json)")
    parser.add_argument("--explain", action="store_true", help="Add RAG-generated explanation for each alert (requires HF_TOKEN for AI explanation)")
    parser.add_argument("--chat", action="store_true", help="After alerts, start conversational mode: ask questions about the alerts (use with --explain or alone; requires HF_TOKEN for AI answers)")
    args = parser.parse_args()

    # Where the project lives (we need this to find knowledge/ and docs/)
    root = Path(__file__).resolve().parent

    # Load everything and run the engine: rules + logs → list of alerts
    rules = load_rules(args.rules)
    logs = load_logs(args.logs)
    alerts = run(rules, logs)

    # If they want explain or chat, we need to build the RAG index first (only if there are alerts)
    index = None
    if (args.explain or args.chat) and alerts:
        from rag import build_index, explain_alert
        kb_path = root / "knowledge" / "security_kb.md"
        docs_paths = [root / "docs" / "shapes.md", root / "logs" / "README.md"]
        index = build_index(rules, logs, kb_path=kb_path, docs_paths=[str(p) for p in docs_paths])

    # Draw a line and then print each alert in a nice block
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
        # If they asked for explanations, grab one from RAG + LLM and show it
        if args.explain and index:
            explanation = explain_alert(a, rules, index, k=4)
            print(f"  Explanation : {explanation}")
    print(f"\n{sep}")
    print(f"  Total alerts: {len(alerts)}")
    print(f"{sep}\n")

    # Chat mode: keep asking for questions until they type exit or quit
    if args.chat and index and alerts:
        from rag import answer_question
        print("\n--- Conversational mode: ask questions about the alerts above. Type 'exit' or 'quit' to stop. ---\n")
        while True:
            try:
                q = input("You: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nGoodbye.")
                break
            if not q:
                continue
            if q.lower() in ("exit", "quit"):
                print("Goodbye.")
                break
            answer = answer_question(q, alerts, rules, index, k=4)
            print(f"System: {answer}\n")


if __name__ == "__main__":
    main()
