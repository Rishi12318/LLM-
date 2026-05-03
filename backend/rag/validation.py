"""Answer validation and hallucination-risk checks."""

from __future__ import annotations

import re
from typing import Dict, Iterable, List

from .prompts import format_context
from .types import RetrievalHit

_WORD_RE = re.compile(r"\b[a-zA-Z0-9']+\b")
_CITATION_RE = re.compile(r"\[(?:source:)?([A-Za-z0-9_:\-./]+)\]")
_SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")


def _tokens(text: str) -> List[str]:
    return [token.lower() for token in _WORD_RE.findall(text)]


def _token_overlap(left: str, right: str) -> float:
    left_tokens = set(_tokens(left))
    right_tokens = set(_tokens(right))
    if not left_tokens or not right_tokens:
        return 0.0
    return len(left_tokens & right_tokens) / len(left_tokens)


def extract_citations(answer: str) -> List[str]:
    return _CITATION_RE.findall(answer or "")


def sentence_support(answer: str, context: str) -> float:
    sentences = [sentence.strip() for sentence in _SENTENCE_RE.split(answer or "") if sentence.strip()]
    if not sentences:
        return 0.0

    supported = 0
    for sentence in sentences:
        if _token_overlap(sentence, context) >= 0.35:
            supported += 1
    return supported / len(sentences)


def validate_answer(answer: str, hits: Iterable[RetrievalHit], minimum_support: float = 0.35) -> Dict[str, object]:
    hits = list(hits)
    context = format_context(hits)
    citations = extract_citations(answer)
    groundedness = sentence_support(answer, context)
    unsupported_ratio = 1.0 - groundedness

    missing_citations = groundedness > 0 and not citations
    is_grounded = groundedness >= minimum_support and not missing_citations

    warnings: List[str] = []
    if not citations:
        warnings.append("No citations found in answer.")
    if groundedness < minimum_support:
        warnings.append("Answer support is weak relative to the retrieved context.")
    if unsupported_ratio > 0.5:
        warnings.append("Potential hallucination risk is elevated.")

    return {
        "is_grounded": is_grounded,
        "groundedness": round(groundedness, 3),
        "unsupported_ratio": round(unsupported_ratio, 3),
        "citations": citations,
        "warnings": warnings,
    }
