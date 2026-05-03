"""Structured prompt builders for grounded RAG answers."""

from __future__ import annotations

from typing import Iterable, List

from .types import RetrievalHit

SYSTEM_PROMPT = """You are a production retrieval-augmented assistant.
Answer only from the provided context.
If the context does not contain the answer, say so explicitly and list what is missing.
Cite supporting chunks in the form [source:chunk_id].
Never invent facts, dates, names, or numbers.
"""

DEVELOPER_PROMPT = """Use a concise, evidence-first style.
Prefer short paragraphs and bullet points when helpful.
If multiple chunks support the same claim, keep the answer grounded in the strongest sources.
"""


def format_context(hits: Iterable[RetrievalHit]) -> str:
    lines: List[str] = []
    for position, hit in enumerate(hits, start=1):
        chunk = hit.chunk
        lines.append(
            f"[{position}] source={chunk.source} chunk_id={chunk.chunk_id} score={hit.score:.3f}\n{chunk.text}"
        )
    return "\n\n".join(lines)


def build_rag_prompt(question: str, hits: Iterable[RetrievalHit]) -> str:
    context = format_context(hits)
    return (
        f"{SYSTEM_PROMPT}\n\n"
        f"{DEVELOPER_PROMPT}\n\n"
        f"Context:\n{context or 'No supporting context found.'}\n\n"
        f"Question: {question}\n\n"
        "Return a grounded answer with citations."
    )


def build_rag_messages(question: str, hits: Iterable[RetrievalHit]) -> List[dict]:
    context = format_context(hits)
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "developer", "content": DEVELOPER_PROMPT},
        {
            "role": "user",
            "content": (
                f"Context:\n{context or 'No supporting context found.'}\n\n"
                f"Question: {question}\n\n"
                "Answer only from the context and include citations."
            ),
        },
    ]
