"""Persistent semantic vector store with optional FAISS acceleration."""

from __future__ import annotations

import json
import logging
import pickle
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List, Sequence

import numpy as np

from .embeddings import EmbeddingBackend
from .types import ChunkRecord, RetrievalHit

logger = logging.getLogger(__name__)

try:
    import faiss  # type: ignore

    FAISS_AVAILABLE = True
except Exception:  # pragma: no cover - optional dependency
    faiss = None
    FAISS_AVAILABLE = False


class VectorStore:
    """Store and retrieve chunked documents."""

    def __init__(
        self,
        storage_dir: str | Path,
        embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        backend: str = "auto",
    ) -> None:
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.embedding_backend = EmbeddingBackend(model_name=embedding_model_name, backend=backend)
        self.chunks_path = self.storage_dir / "chunks.json"
        self.embeddings_path = self.storage_dir / "embeddings.npy"
        self.vectorizer_path = self.storage_dir / "vectorizer.pkl"
        self.state_path = self.storage_dir / "store_state.json"
        self.faiss_path = self.storage_dir / "index.faiss"
        self.chunks: List[Dict[str, Any]] = []
        self.embeddings: np.ndarray | None = None
        self.faiss_index = None
        self._load()

    def _load(self) -> None:
        if self.chunks_path.exists():
            self.chunks = json.loads(self.chunks_path.read_text(encoding="utf-8"))

        if self.vectorizer_path.exists() and self.embedding_backend.backend == "tfidf":
            with self.vectorizer_path.open("rb") as handle:
                self.embedding_backend.vectorizer = pickle.load(handle)

        if self.embeddings_path.exists():
            self.embeddings = np.load(self.embeddings_path)

        if FAISS_AVAILABLE and self.faiss_path.exists():
            self.faiss_index = faiss.read_index(str(self.faiss_path))

        if self.state_path.exists():
            state = json.loads(self.state_path.read_text(encoding="utf-8"))
            backend = state.get("backend")
            if backend:
                self.embedding_backend.backend = backend
            model_name = state.get("model_name")
            if model_name:
                self.embedding_backend.model_name = model_name

    def _persist(self) -> None:
        self.chunks_path.write_text(json.dumps(self.chunks, ensure_ascii=False, indent=2), encoding="utf-8")
        self.state_path.write_text(
            json.dumps(
                {
                    "backend": self.embedding_backend.backend,
                    "model_name": self.embedding_backend.model_name,
                    "count": len(self.chunks),
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        if self.embeddings is not None:
            np.save(self.embeddings_path, self.embeddings)
        if self.embedding_backend.backend == "tfidf" and self.embedding_backend.vectorizer is not None:
            with self.vectorizer_path.open("wb") as handle:
                pickle.dump(self.embedding_backend.vectorizer, handle)
        if FAISS_AVAILABLE and self.faiss_index is not None:
            faiss.write_index(self.faiss_index, str(self.faiss_path))

    def clear(self) -> None:
        self.chunks = []
        self.embeddings = None
        self.faiss_index = None
        for path in [self.chunks_path, self.embeddings_path, self.vectorizer_path, self.state_path, self.faiss_path]:
            if path.exists():
                path.unlink()

    def add_chunks(self, chunks: Sequence[ChunkRecord | Dict[str, Any]]) -> None:
        for chunk in chunks:
            self.chunks.append(asdict(chunk) if hasattr(chunk, "__dataclass_fields__") else dict(chunk))
        self.rebuild()

    def rebuild(self) -> None:
        if not self.chunks:
            self.clear()
            return

        texts = [chunk["text"] for chunk in self.chunks]
        self.embeddings = self.embedding_backend.fit_transform(texts)
        self._build_faiss_index()
        self._persist()

    def _build_faiss_index(self) -> None:
        if not FAISS_AVAILABLE or self.embeddings is None or self.embeddings.size == 0:
            self.faiss_index = None
            return

        matrix = self._normalize_matrix(self.embeddings)
        dim = matrix.shape[1]
        index = faiss.IndexFlatIP(dim)
        index.add(matrix.astype(np.float32))
        self.faiss_index = index
        self.embeddings = matrix

    @staticmethod
    def _normalize_matrix(matrix: np.ndarray) -> np.ndarray:
        dense = np.asarray(matrix, dtype=np.float32)
        if dense.ndim == 1:
            dense = dense.reshape(1, -1)
        norms = np.linalg.norm(dense, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        return dense / norms

    def search(self, query: str, top_k: int = 5) -> List[RetrievalHit]:
        if not self.chunks:
            return []

        if self.embeddings is None:
            self.rebuild()

        if self.embeddings is None or self.embeddings.size == 0:
            return []

        query_vector = self.embedding_backend.encode([query])
        query_vector = self._normalize_matrix(query_vector)

        if FAISS_AVAILABLE and self.faiss_index is not None:
            scores, indices = self.faiss_index.search(query_vector.astype(np.float32), min(top_k, len(self.chunks)))
            ranked: List[RetrievalHit] = []
            for score, idx in zip(scores[0], indices[0]):
                if idx < 0:
                    continue
                ranked.append(RetrievalHit(chunk=ChunkRecord(**self.chunks[idx]), score=float(score)))
            return ranked

        matrix = self._normalize_matrix(self.embeddings)
        scores = matrix @ query_vector[0]
        ranked_indices = np.argsort(scores)[::-1][:top_k]
        return [RetrievalHit(chunk=ChunkRecord(**self.chunks[idx]), score=float(scores[idx])) for idx in ranked_indices]

    def stats(self) -> Dict[str, Any]:
        return {
            "document_count": len({chunk["document_id"] for chunk in self.chunks}),
            "chunk_count": len(self.chunks),
            "backend": self.embedding_backend.backend,
            "model_name": self.embedding_backend.model_name,
            "faiss_enabled": FAISS_AVAILABLE and self.faiss_index is not None,
        }
