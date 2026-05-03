"""Chunking helpers for documents and transcripts."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence

from .types import ChunkRecord


@dataclass(frozen=True)
class ChunkingConfig:
    """Chunking strategy tuned for retrieval quality."""

    chunk_size_words: int = 220
    chunk_overlap_words: int = 40
    min_chunk_words: int = 25


_WORD_RE = re.compile(r"\s+")
_SENTENCE_BOUNDARY_RE = re.compile(r"(?<=[.!?])\s+")


def normalize_text(text: str) -> str:
    """Normalize whitespace while preserving paragraph boundaries."""

    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = "\n".join(line.strip() for line in text.split("\n"))
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def split_sentences(text: str) -> List[str]:
    """Lightweight sentence splitter for chunk pre-processing."""

    cleaned = normalize_text(text)
    if not cleaned:
        return []
    parts = _SENTENCE_BOUNDARY_RE.split(cleaned)
    return [part.strip() for part in parts if part.strip()]


def chunk_text(text: str, config: ChunkingConfig | None = None) -> List[str]:
    """Split a document into overlapping word chunks."""

    config = config or ChunkingConfig()
    sentences = split_sentences(text)
    if not sentences:
        return []

    chunks: List[str] = []
    current: List[str] = []
    current_size = 0

    def flush_chunk() -> None:
        nonlocal current, current_size
        if current and current_size >= config.min_chunk_words:
            chunks.append(" ".join(current).strip())
        current = []
        current_size = 0

    for sentence in sentences:
        words = sentence.split()
        if not words:
            continue

        if current_size + len(words) <= config.chunk_size_words:
            current.extend(words)
            current_size += len(words)
            continue

        flush_chunk()

        while len(words) > config.chunk_size_words:
            chunks.append(" ".join(words[: config.chunk_size_words]).strip())
            words = words[config.chunk_size_words - config.chunk_overlap_words :]

        current = words[:]
        current_size = len(current)

    flush_chunk()

    if not chunks and current:
        chunks.append(" ".join(current).strip())

    return chunks


def build_document_chunks(
    document_id: str,
    source_name: str,
    text: str,
    metadata: Dict[str, Any] | None = None,
    config: ChunkingConfig | None = None,
) -> List[ChunkRecord]:
    """Create chunk records for a document or transcript."""

    config = config or ChunkingConfig()
    normalized = normalize_text(text)
    chunks = chunk_text(normalized, config=config)
    records: List[ChunkRecord] = []

    for index, chunk in enumerate(chunks):
        chunk_id = f"{document_id}:{index:04d}"
        records.append(
            ChunkRecord(
                chunk_id=chunk_id,
                document_id=document_id,
                source=source_name,
                text=chunk,
                chunk_index=index,
                metadata={**(metadata or {}), "word_count": len(chunk.split())},
            )
        )

    return records


def transcript_segments_to_text(segments: Sequence[Dict[str, Any]]) -> str:
    """Convert transcript segments into retrieval-friendly prose."""

    lines: List[str] = []
    for segment in segments:
        speaker = segment.get("speaker", "Speaker")
        start = segment.get("start", 0.0)
        end = segment.get("end", 0.0)
        original = segment.get("original") or segment.get("text") or ""
        english = segment.get("english")
        line = f"{speaker} [{start:.2f}-{end:.2f}]: {original}".strip()
        if english and english != original:
            line += f" | EN: {english}"
        lines.append(line)
    return "\n".join(lines)


def load_text_from_file(file_path: str | Path) -> str:
    """Load text, markdown, or transcript JSON into plain text."""

    path = Path(file_path)
    suffix = path.suffix.lower()

    if suffix in {".txt", ".md", ".markdown"}:
        return path.read_text(encoding="utf-8")

    if suffix == ".json":
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, dict) and "segments" in payload:
            return transcript_segments_to_text(payload["segments"])
        return json.dumps(payload, ensure_ascii=False, indent=2)

    return path.read_text(encoding="utf-8")
