"""Embedding backends for semantic retrieval."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from functools import lru_cache
from typing import Iterable, List, Sequence

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def _load_sentence_transformer(model_name: str):
    from sentence_transformers import SentenceTransformer

    logger.info("Loading sentence transformer model %s", model_name)
    return SentenceTransformer(model_name)


@dataclass
class EmbeddingBackend:
    """Encodes texts with a sentence transformer or a local TF-IDF fallback."""

    model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    backend: str = "auto"
    max_features: int = 4096

    def __post_init__(self) -> None:
        self.vectorizer: TfidfVectorizer | None = None
        self.backend = self._resolve_backend(self.backend)

    def _resolve_backend(self, backend: str) -> str:
        if backend != "auto":
            return backend

        try:
            import sentence_transformers  # noqa: F401

            return "sentence-transformers"
        except Exception:
            logger.warning("SentenceTransformer unavailable; using TF-IDF fallback")
            return "tfidf"

    def fit_transform(self, texts: Sequence[str]) -> np.ndarray:
        if self.backend == "tfidf":
            self.vectorizer = TfidfVectorizer(
                stop_words="english",
                ngram_range=(1, 2),
                max_features=self.max_features,
            )
            matrix = self.vectorizer.fit_transform(list(texts))
            return self._to_dense(matrix)

        return self.encode(texts)

    def encode(self, texts: Sequence[str]) -> np.ndarray:
        if not texts:
            return np.zeros((0, 0), dtype=np.float32)

        if self.backend == "tfidf":
            if self.vectorizer is None:
                raise RuntimeError("TF-IDF backend must be fit before encoding query text")
            matrix = self.vectorizer.transform(list(texts))
            return self._to_dense(matrix)

        model = _load_sentence_transformer(self.model_name)
        embeddings = model.encode(
            list(texts),
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        return np.asarray(embeddings, dtype=np.float32)

    @staticmethod
    def _to_dense(matrix) -> np.ndarray:
        dense = matrix.toarray() if hasattr(matrix, "toarray") else np.asarray(matrix)
        dense = dense.astype(np.float32, copy=False)
        norms = np.linalg.norm(dense, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        return dense / norms
