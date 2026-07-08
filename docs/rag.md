# RAG (Retrieval-Augmented Generation) for Alerts

The `--explain` flag adds a human-readable explanation to each alert. The `--chat` flag starts a **conversational mode** after alerts: you can ask questions about the alerts (e.g. "Why did alert 1 trigger?", "What damage can this command cause?") and get answers from the same RAG index and LLM.

## How to run

**Explanations only:**
```bash
python main.py --rules rules --logs logs/sample.json --explain
```

**Conversational mode (ask questions after alerts):**
```bash
python main.py --rules rules --logs logs/sample.json --chat
```

You can combine both: `--explain --chat` shows explanations for each alert, then enters the question loop.

In chat mode, type your question and press Enter. Type `exit` or `quit` to stop. Answers use the security knowledge base, rules, and logs as context.

## Without an API key

If `HF_TOKEN` is not set, the explanation is a short fallback message. The RAG index still runs so the pipeline is ready for an LLM.

## With Hugging Face (free)

The app uses **Hugging Face Inference API** for explanations and chat — no paid API required.

1. Create a free token at [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens).
2. Set it in your environment:

```bash
set HF_TOKEN=your-token
```

3. Run with `--explain` and/or `--chat`:

```bash
python main.py --rules rules --logs logs/sample.json --explain
python main.py --rules rules --logs logs/sample.json --chat
```

Default model: `HuggingFaceH4/zephyr-7b-beta`. To use another model, set `RAG_HF_MODEL` (e.g. `microsoft/Phi-3-mini-4k-instruct`).

**Note:** Set `HF_TOKEN` in `.env` for AI-powered explanations and chat.

## What gets indexed

- **knowledge/security_kb.md** — Command/pattern → what it does, why dangerous, attack type.
- **Rules** (YAML) — Rule id, name, description, patterns.
- **Logs** — The log entries from the current run.
- **Docs** — docs/shapes.md, logs/README.md.

## Dependencies

See `requirements.txt`: `sentence-transformers`, `chromadb`, `huggingface_hub`, `python-dotenv`. Install with:

```bash
pip install -r requirements.txt
```

First run with `--explain` may download the embedding model (all-MiniLM-L6-v2) once.
