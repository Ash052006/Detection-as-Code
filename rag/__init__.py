# RAG: we search the knowledge base + rules + logs and then ask an LLM to explain or answer questions
from rag.index_builder import build_index
from rag.explain import explain_alert, answer_question

__all__ = ["build_index", "explain_alert", "answer_question"]
