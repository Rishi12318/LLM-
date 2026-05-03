"""Shared types for the RAG stack."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class ChunkRecord:
    """A single retrievable text chunk."""

    chunk_id: str
    document_id: str
    source: str
    text: str
    chunk_index: int
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RetrievalHit:
    """A ranked chunk returned by retrieval."""

    chunk: ChunkRecord
    score: float


@dataclass
class EvaluationCase:
    """A single evaluation sample for RAG quality checks."""

    question: str
    context: str
    reference_answer: str
    candidate_answer: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EvaluationMetrics:
    """Metric bundle for one evaluation case."""

    relevance: float
    correctness: float
    consistency: float
    groundedness: float
    overall: float
    notes: Dict[str, Any] = field(default_factory=dict)
