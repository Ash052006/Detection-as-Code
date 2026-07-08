"""
Build a searchable index from the knowledge base, rules, logs, and docs. Used for RAG (explain + chat).
"""

from pathlib import Path
from typing import Any

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer


def _chunk_kb(kb_path: str | Path) -> list[str]:
    # Split the KB file into chunks — one chunk per ## section so we can search by topic
    path = Path(kb_path)
    if not path.is_file():
        return []
    text = path.read_text(encoding="utf-8")
    chunks = []
    current = []
    for line in text.splitlines():
        if line.strip().startswith("## "):
            if current:
                chunks.append("\n".join(current))
            current = [line]
        else:
            current.append(line)
    if current:
        chunks.append("\n".join(current))
    return chunks


def _chunk_rules(rules: list[dict[str, Any]]) -> list[str]:
    # Turn each rule into one text chunk (id, name, description, patterns) so we can find it later
    chunks = []
    for r in rules:
        cond = r.get("condition", {})
        patterns = cond.get("patterns", [])
        parts = [
            f"Rule ID: {r.get('id', '')}",
            f"Name: {r.get('name', '')}",
            f"Description: {r.get('description', '')}",
            f"Severity: {r.get('severity', '')}",
            f"Patterns: {', '.join(patterns)}",
        ]
        chunks.append("\n".join(parts))
    return chunks


def _chunk_logs(logs: list[dict[str, Any]]) -> list[str]:
    # One short chunk per log entry so we can pull in relevant log lines when answering
    chunks = []
    for log in logs:
        msg = log.get("message", "")
        ts = log.get("timestamp", "")
        source = log.get("source", "")
        chunks.append(f"Log entry: {msg} | timestamp: {ts} | source: {source}")
    return chunks


def _chunk_doc(doc_path: str | Path) -> list[str]:
    # Same idea as the KB — split a markdown doc by ## sections
    path = Path(doc_path)
    if not path.is_file():
        return []
    text = path.read_text(encoding="utf-8")
    chunks = []
    current = []
    for line in text.splitlines():
        if line.strip().startswith("## "):
            if current:
                chunks.append("\n".join(current))
            current = [line]
        else:
            current.append(line)
    if current:
        chunks.append("\n".join(current))
    return chunks


def build_index(
    rules: list[dict[str, Any]],
    logs: list[dict[str, Any]],
    kb_path: str | Path = "knowledge/security_kb.md",
    docs_paths: list[str | Path] | None = None,
    embedding_model: str = "all-MiniLM-L6-v2",
) -> Any:
    if docs_paths is None:
        docs_paths = ["docs/shapes.md", "logs/README.md"]

    all_chunks = []
    all_ids = []

    # Add KB chunks with ids like kb_0, kb_1, ...
    kb_chunks = _chunk_kb(kb_path)
    for i, c in enumerate(kb_chunks):
        all_chunks.append(c)
        all_ids.append(f"kb_{i}")

    # Add rule chunks
    rule_chunks = _chunk_rules(rules)
    for i, c in enumerate(rule_chunks):
        all_chunks.append(c)
        all_ids.append(f"rule_{i}")

    # Add log chunks
    log_chunks = _chunk_logs(logs)
    for i, c in enumerate(log_chunks):
        all_chunks.append(c)
        all_ids.append(f"log_{i}")

    # Add each doc file's chunks
    for doc_path in docs_paths:
        for i, c in enumerate(_chunk_doc(doc_path)):
            all_chunks.append(c)
            all_ids.append(f"doc_{Path(doc_path).name}_{i}")

    if not all_chunks:
        return _EmptyIndex()

    # Turn text into numbers (embeddings) so we can do similarity search
    model = SentenceTransformer(embedding_model)
    embeddings = model.encode(all_chunks).tolist()

    # Store everything in ChromaDB so we can query "give me the k closest chunks to this question"
    client = chromadb.Client(Settings(anonymized_telemetry=False))
    coll = client.get_or_create_collection("rag", metadata={"description": "Security RAG"})
    coll.add(ids=all_ids, documents=all_chunks, embeddings=embeddings)

    # Wrap the collection + model in a small object that has a retrieve(query, k) method
    class Index:
        def __init__(self, collection, model):
            self._coll = collection
            self._model = model

        def retrieve(self, query: str, k: int = 4) -> list[str]:
            # Turn the query into numbers, then ask Chroma for the k nearest chunks
            q_emb = self._model.encode([query]).tolist()
            n = self._coll.count()
            res = self._coll.query(query_embeddings=q_emb, n_results=min(k, n) if n else 0)
            docs = res.get("documents", [[]])
            return docs[0] if docs else []

    return Index(coll, model)


class _EmptyIndex:
    # When there's nothing to index, retrieve just returns an empty list (no crashes)
    def retrieve(self, query: str, k: int = 4) -> list[str]:
        return []
