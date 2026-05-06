"""High-level RAG orchestration for ingestion, retrieval, and grounded responses."""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence

from .chunking import ChunkingConfig, build_document_chunks, load_text_from_file, transcript_segments_to_text
from .evaluation import EvaluationCase, run_evaluation_suite
from .prompts import build_rag_messages, build_rag_prompt, build_summarization_messages
from .types import ChunkRecord, RetrievalHit
from .validation import validate_answer
from .vector_store import VectorStore

logger = logging.getLogger(__name__)


class RAGService:
    """Ingest documents, retrieve supporting chunks, and validate responses."""

    def __init__(
        self,
        storage_dir: str | Path,
        embedding_backend: str = "auto",
        embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        chunking: ChunkingConfig | None = None,
    ) -> None:
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.chunking = chunking or ChunkingConfig()
        self.vector_store = VectorStore(
            self.storage_dir / "vector_store",
            embedding_model_name=embedding_model_name,
            backend=embedding_backend,
        )
        self.manifest_path = self.storage_dir / "documents.json"
        self.documents = self._load_manifest()

    def _load_manifest(self) -> List[Dict[str, Any]]:
        if self.manifest_path.exists():
            return json.loads(self.manifest_path.read_text(encoding="utf-8"))
        return []

    def _persist_manifest(self) -> None:
        self.manifest_path.write_text(json.dumps(self.documents, ensure_ascii=False, indent=2), encoding="utf-8")

    def ingest_text(
        self,
        document_id: str,
        source_name: str,
        text: str,
        metadata: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        chunks = build_document_chunks(document_id, source_name, text, metadata=metadata, config=self.chunking)
        self.vector_store.add_chunks(chunks)
        document_record = {
            "document_id": document_id,
            "source_name": source_name,
            "ingested_at": datetime.utcnow().isoformat(),
            "metadata": metadata or {},
            "chunk_count": len(chunks),
        }
        self.documents = [doc for doc in self.documents if doc.get("document_id") != document_id]
        self.documents.append(document_record)
        self._persist_manifest()
        return document_record

    def ingest_file(
        self,
        file_path: str | Path,
        document_id: str | None = None,
        metadata: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        path = Path(file_path)
        document_id = document_id or path.stem
        text = load_text_from_file(path)
        return self.ingest_text(document_id, path.name, text, metadata=metadata)

    def ingest_files(self, file_paths: Sequence[str | Path]) -> List[Dict[str, Any]]:
        return [self.ingest_file(file_path) for file_path in file_paths]

    def ingest_transcription(
        self,
        job_id: str,
        segments: Sequence[Dict[str, Any]],
        metadata: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        text = transcript_segments_to_text(segments)
        payload_metadata = {
            **(metadata or {}),
            "source": "transcription",
            "job_id": job_id,
            "segment_count": len(segments),
        }
        return self.ingest_text(f"transcript-{job_id}", f"transcript-{job_id}", text, metadata=payload_metadata)

    def retrieve(self, question: str, top_k: int = 5) -> List[RetrievalHit]:
        return self.vector_store.search(question, top_k=top_k)

    def _grounded_answer(self, question: str, hits: Sequence[RetrievalHit]) -> str:
        if not hits:
            return "No supporting context was found for that question."

        lines = [
            f"{hit.chunk.text.strip()} [{hit.chunk.source}:{hit.chunk.chunk_id}]"
            for hit in hits[: min(3, len(hits))]
        ]
        answer = " ".join(lines)
        return answer[:1500]

    def query(
        self,
        question: str,
        top_k: int = 5,
        generator: Callable[[List[dict], Sequence[RetrievalHit]], str] | None = None,
        history: List[dict] | None = None,
    ) -> Dict[str, Any]:
        hits = self.retrieve(question, top_k=top_k)
        prompt = build_rag_prompt(question, hits)
        messages = build_rag_messages(question, hits)
        
        # Inject conversation history if provided
        if history:
            # Keep system and developer prompts at the top, inject history before user question
            system_msgs = messages[:-1]
            user_msg = messages[-1:]
            messages = system_msgs + history + user_msg

        answer = generator(messages, hits) if generator else self._grounded_answer(question, hits)
        validation = validate_answer(answer, hits)

        return {
            "question": question,
            "answer": answer,
            "prompt": prompt,
            "messages": messages,
            "retrieval": [
                {
                    "chunk_id": hit.chunk.chunk_id,
                    "document_id": hit.chunk.document_id,
                    "source": hit.chunk.source,
                    "text": hit.chunk.text,
                    "score": round(hit.score, 4),
                    "metadata": hit.chunk.metadata,
                }
                for hit in hits
            ],
            "validation": validation,
            "store": self.vector_store.stats(),
        }

    def summarize(
        self,
        text: str,
        generator: Callable[[List[dict], Sequence[RetrievalHit]], str] | None = None,
    ) -> str:
        """Generate a high-level summary of the provided text."""
        messages = build_summarization_messages(text)
        if generator:
            # Summarization doesn't need retrieval hits for grounding, but generator expects them
            return generator(messages, [])
        
        # Fallback if no generator
        return "Summary generation requires an active LLM generator (e.g., Ollama)."

    def evaluate(self, cases: Sequence[EvaluationCase] | None = None) -> Dict[str, Any]:
        return run_evaluation_suite(cases)
