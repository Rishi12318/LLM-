"""Evaluation framework for RAG outputs."""

from __future__ import annotations

from dataclasses import asdict
from typing import Dict, Iterable, List, Sequence

from .types import EvaluationCase, EvaluationMetrics
from .validation import validate_answer


def _tokens(text: str) -> set[str]:
    return {token.lower() for token in text.replace("/", " ").split() if token}


def _token_f1(prediction: str, reference: str) -> float:
    pred_tokens = _tokens(prediction)
    ref_tokens = _tokens(reference)
    if not pred_tokens or not ref_tokens:
        return 0.0

    overlap = len(pred_tokens & ref_tokens)
    precision = overlap / len(pred_tokens)
    recall = overlap / len(ref_tokens)
    if precision + recall == 0:
        return 0.0
    return 2 * precision * recall / (precision + recall)


def _jaccard(left: str, right: str) -> float:
    left_tokens = _tokens(left)
    right_tokens = _tokens(right)
    if not left_tokens or not right_tokens:
        return 0.0
    return len(left_tokens & right_tokens) / len(left_tokens | right_tokens)


def evaluate_case(case: EvaluationCase) -> EvaluationMetrics:
    answer = case.candidate_answer or case.reference_answer
    relevance = 0.5 * _jaccard(case.question, answer) + 0.5 * _jaccard(case.context, answer)
    correctness = _token_f1(answer, case.reference_answer)
    groundedness = _jaccard(case.context, answer)
    validation = validate_answer(answer, [])
    consistency = max(0.0, 1.0 - abs(correctness - groundedness))
    overall = round((0.30 * relevance) + (0.35 * correctness) + (0.20 * consistency) + (0.15 * groundedness), 3)

    return EvaluationMetrics(
        relevance=round(relevance, 3),
        correctness=round(correctness, 3),
        consistency=round(consistency, 3),
        groundedness=round(groundedness, 3),
        overall=overall,
        notes={"question": case.question, "metadata": case.metadata, "warnings": validation["warnings"]},
    )


SAMPLE_EVALUATION_CASES: List[EvaluationCase] = [
    EvaluationCase(
        question="What did the team decide about model evaluation?",
        context="The team agreed to add retrieval metrics, citation checks, and a regression set for weekly review.",
        reference_answer="They decided to add retrieval metrics, citation checks, and a regression set for weekly review.",
        candidate_answer="They agreed to add retrieval metrics, citation checks, and a weekly regression set.",
        metadata={"id": "eval-001"},
    ),
    EvaluationCase(
        question="How is the system made more reliable?",
        context="The system now validates citations, logs retrieval scores, and caches embeddings on disk.",
        reference_answer="It is made more reliable by validating citations, logging retrieval scores, and caching embeddings on disk.",
        candidate_answer="It validates citations, logs retrieval scores, and caches embeddings on disk.",
        metadata={"id": "eval-002"},
    ),
    EvaluationCase(
        question="What does the retrieval layer use?",
        context="The retrieval layer uses sentence-transformer embeddings with a FAISS fallback or TF-IDF if needed.",
        reference_answer="It uses sentence-transformer embeddings with a FAISS fallback and a TF-IDF fallback when needed.",
        candidate_answer="It uses sentence-transformer embeddings with a FAISS fallback and a TF-IDF fallback when needed.",
        metadata={"id": "eval-003"},
    ),
]


def run_evaluation_suite(cases: Sequence[EvaluationCase] | None = None) -> Dict[str, object]:
    cases = list(cases or SAMPLE_EVALUATION_CASES)
    results = []
    totals = {"relevance": 0.0, "correctness": 0.0, "consistency": 0.0, "groundedness": 0.0, "overall": 0.0}

    for case in cases:
        metrics = evaluate_case(case)
        result = {**case.metadata, **asdict(metrics)}
        results.append(result)
        for key in totals:
            totals[key] += getattr(metrics, key)

    count = max(len(cases), 1)
    summary = {key: round(value / count, 3) for key, value in totals.items()}

    return {
        "summary": summary,
        "results": results,
        "count": len(cases),
    }
