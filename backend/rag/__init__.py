"""Retrieval, generation, validation, and evaluation utilities."""

from .chunking import ChunkRecord, ChunkingConfig, build_document_chunks, chunk_text
from .evaluation import EvaluationCase, EvaluationMetrics, SAMPLE_EVALUATION_CASES, evaluate_case, run_evaluation_suite
from .generator import OllamaGenerator, SimpleContextGenerator, get_default_generator
from .prompts import build_rag_messages, build_rag_prompt
from .service import RAGService
from .validation import validate_answer
from .vector_store import VectorStore

__all__ = [
    "ChunkRecord",
    "ChunkingConfig",
    "build_document_chunks",
    "chunk_text",
    "EvaluationCase",
    "EvaluationMetrics",
    "SAMPLE_EVALUATION_CASES",
    "evaluate_case",
    "run_evaluation_suite",
    "OllamaGenerator",
    "SimpleContextGenerator",
    "get_default_generator",
    "build_rag_messages",
    "build_rag_prompt",
    "RAGService",
    "validate_answer",
    "VectorStore",
]
