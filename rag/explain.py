"""
Generate explanations for alerts and answer follow-up questions using RAG + an LLM (Hugging Face).
"""

import os
from pathlib import Path
from typing import Any, Callable


def _ensure_env_loaded() -> None:
    # Make sure we've loaded the .env file so HF_TOKEN is available (fine to call more than once)
    env_path = Path(__file__).resolve().parent.parent / ".env"
    if env_path.exists():
        from dotenv import load_dotenv
        load_dotenv(env_path, override=True)


def _query_for_alert(alert: dict[str, Any], rules_by_id: dict[str, dict]) -> str:
    # Build a search string from the alert and its rule so we can find relevant chunks in the index
    rule_id = alert.get("rule_id", "")
    rule = rules_by_id.get(rule_id, {})
    msg = alert.get("log", {}).get("message", "")
    name = rule.get("name", "")
    desc = rule.get("description", "")
    return f"{rule_id} {name} {desc} {msg}"


def _call_huggingface(system: str, user: str) -> tuple[str, str]:
    # Call Hugging Face's API to get a reply. Returns (reply_text, error_string). Error is empty on success.
    _ensure_env_loaded()
    raw = os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_API_KEY") or ""
    token = raw.strip().strip('"').strip("'")
    if not token or token.lower() == "your_huggingface_token_here":
        return "", "no_token"

    # Pick a model — avoid the old zephyr one that doesn't work on the free tier; default to something that does
    raw_model = (os.environ.get("RAG_HF_MODEL") or "").strip()
    if "zephyr" in raw_model.lower() or not raw_model:
        raw_model = "google/gemma-2-2b-it"

    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]

    # The router needs to know which provider to use — :cheapest picks one that works with free credits
    fallback_models = [
        "Qwen/Qwen2.5-7B-Instruct:cheapest",
        "meta-llama/Llama-3.1-8B-Instruct:cheapest",
        "Qwen/Qwen2.5-7B-Instruct",
        "meta-llama/Llama-3.1-8B-Instruct",
    ]
    models_to_try = [raw_model] + [m for m in fallback_models if m != raw_model]

    try:
        import json
        import urllib.error
        import urllib.request
        url = "https://router.huggingface.co/v1/chat/completions"
        last_err = None
        for try_model in models_to_try:
            try:
                msgs = list(messages)
                req_body = json.dumps({
                    "model": try_model,
                    "messages": msgs,
                    "max_tokens": 200,
                    "temperature": 0.3,
                }).encode("utf-8")
                req = urllib.request.Request(
                    url,
                    data=req_body,
                    headers={
                        "Authorization": f"Bearer {token}",
                        "Content-Type": "application/json",
                    },
                    method="POST",
                )
                with urllib.request.urlopen(req, timeout=60) as resp:
                    out = json.loads(resp.read().decode())
                choices = out.get("choices") or []
                if choices and isinstance(choices[0].get("message"), dict):
                    content = (choices[0]["message"].get("content") or "").strip()
                    if content:
                        return content, ""
            except urllib.error.HTTPError as inner:
                body = ""
                try:
                    body = inner.read().decode()[:200]
                except Exception:
                    pass
                last_err = Exception(f"HTTP {inner.code}: {body or inner.reason}")
                continue
            except Exception as inner:
                last_err = inner
                continue
        if last_err is not None:
            raise last_err
    except Exception as e:
        err = str(e)
        # 403 usually means the token doesn't have the right permission — tell them how to fix it
        if "403" in err or "Forbidden" in err:
            return "", (
                "Token missing permission. Create a token at https://huggingface.co/settings/tokens "
                'with "Inference" or "Inference Providers" (e.g. "Make calls to Inference Providers") enabled.'
            )
        return "", err
    return "", "unknown"


def explain_alert(
    alert: dict[str, Any],
    rules: list[dict[str, Any]],
    index: Any,
    k: int = 4,
    llm_fn: Callable[[str, str], str] | None = None,
) -> str:
    # Look up the rule that fired and build a query so we can pull relevant bits from the index
    rules_by_id = {r["id"]: r for r in rules if r.get("id")}
    query = _query_for_alert(alert, rules_by_id)
    chunks = index.retrieve(query, k=k)
    context = "\n\n".join(chunks) if chunks else "No additional context."

    rule_id = alert.get("rule_id", "")
    severity = alert.get("severity", "")
    message = alert.get("log", {}).get("message", "")

    # Tell the LLM what we want: a short, clear explanation for an analyst
    system = (
        "You are explaining a security detection alert to an analyst or beginner. "
        "Use the provided context to explain what the command or pattern does, why it is dangerous, "
        "and what type of attack it may represent. Keep the answer to 2-4 short sentences. Be factual and clear."
    )
    user = (
        f"Alert: Rule ID = {rule_id}, Severity = {severity}. Log message: {message}\n\n"
        f"Relevant context:\n{context}\n\n"
        "Provide a short explanation: what does this do, why is it dangerous, and what should the user do?"
    )

    if llm_fn is not None:
        return llm_fn(system, user) or _fallback_explanation(message, context)

    # Use Hugging Face (free with a token); fallback message if no token or API error
    response, hf_err = _call_huggingface(system, user)
    if response:
        return response
    if hf_err and hf_err != "no_token":
        return _fallback_explanation(message, context) + f" (HF API: {hf_err[:80]})"
    return _fallback_explanation(message, context)


def _fallback_explanation(message: str, context: str) -> str:
    # When we can't reach any LLM, show a snippet and tell them to set up the token
    snippet = message[:100] + ("..." if len(message) > 100 else "")
    return (
        f"Detected pattern in log: \"{snippet}\". "
        "Set HF_TOKEN (Hugging Face, free at huggingface.co/settings/tokens) for an AI-generated explanation."
    )


def answer_question(
    question: str,
    alerts: list[dict[str, Any]],
    rules: list[dict[str, Any]],
    index: Any,
    k: int = 4,
    llm_fn: Callable[[str, str], str] | None = None,
) -> str:
    if not question.strip():
        return "Please ask a question about the alerts."

    # Build a short list of what alerts we have so the LLM has context
    alerts_summary = []
    for i, a in enumerate(alerts, 1):
        msg = a.get("log", {}).get("message", "")[:80]
        alerts_summary.append(f"Alert #{i}: Rule {a.get('rule_id', '')} | {msg}...")
    alerts_context = "\n".join(alerts_summary)

    # Search the index for chunks that relate to their question + the current alerts
    query = f"{question} {alerts_context}"
    chunks = index.retrieve(query, k=k)
    context = "\n\n".join(chunks) if chunks else "No additional context."

    system = (
        "You are a security analyst assistant. The user is asking questions about security alerts that were just detected. "
        "Use the provided context (from a security knowledge base, detection rules, and logs) to answer clearly and concisely. "
        "Keep answers to 2-5 sentences unless the user asks for more detail. Be factual."
    )
    user = (
        f"Current alerts summary:\n{alerts_context}\n\n"
        f"Relevant context from knowledge base and rules:\n{context}\n\n"
        f"User question: {question}\n\n"
        "Answer the user's question based on the context above."
    )

    if llm_fn is not None:
        return llm_fn(system, user) or _fallback_chat(question)

    response, hf_err = _call_huggingface(system, user)
    if response:
        return response
    if hf_err and hf_err != "no_token":
        return _fallback_chat(question) + f" (HF API: {hf_err[:80]})"
    return _fallback_chat(question)


def _fallback_chat(question: str) -> str:
    # No LLM available — echo back a bit of their question and point them to HF token setup
    q = question.strip()[:60] + ("..." if len(question.strip()) > 60 else "")
    return (
        f"I can't answer \"{q}\" without an LLM. "
        "Set HF_TOKEN (Hugging Face, free at huggingface.co/settings/tokens) for conversational investigation."
    )
