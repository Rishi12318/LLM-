"""LLM generation backends for grounded RAG answers."""

from __future__ import annotations

import logging
from typing import Any, List, Optional, Sequence

import requests

from .types import RetrievalHit

logger = logging.getLogger(__name__)


class OllamaGenerator:
    """Wraps Ollama API for RAG answer generation.
    
    Expects Ollama to be running locally at base_url (default: http://localhost:11434).
    Use: ollama run mistral (or other model)
    """

    def __init__(
        self,
        model_name: str = "mistral",
        base_url: str = "http://localhost:11434",
        temperature: float = 0.3,
        timeout: float = 60.0,
    ):
        """Initialize Ollama generator.
        
        Args:
            model_name: Model to use (e.g., 'mistral', 'neural-chat', 'orca-mini')
            base_url: Ollama API base URL
            temperature: Sampling temperature (0.0-1.0), lower = more deterministic
            timeout: Request timeout in seconds
        """
        self.model_name = model_name
        self.base_url = base_url.rstrip("/")
        self.temperature = max(0.0, min(temperature, 1.0))
        self.timeout = timeout
        self._available = None

    def is_available(self) -> bool:
        """Check if Ollama is running and model is available."""
        if self._available is not None:
            return self._available

        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=5,
            )
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [m.get("name", "").split(":")[0] for m in models]
                self._available = self.model_name in model_names
                if not self._available:
                    logger.warning(
                        f"Ollama model '{self.model_name}' not available. "
                        f"Available: {model_names}. "
                        f"Run: ollama run {self.model_name}"
                    )
                return self._available
        except (requests.RequestException, Exception) as e:
            logger.debug(f"Ollama not available: {e}")
            self._available = False
            return False

    def generate(self, messages: List[dict], hits: Sequence[RetrievalHit]) -> str:
        """Generate answer from messages using Ollama.
        
        Args:
            messages: List of role/content dicts (system, developer, user)
            hits: Retrieved context chunks (unused but part of generator interface)
            
        Returns:
            Generated answer text with citations
        """
        if not self.is_available():
            raise RuntimeError(
                f"Ollama not available at {self.base_url} or model '{self.model_name}' not found. "
                f"Start Ollama: ollama run {self.model_name}"
            )

        try:
            # Convert our message format to Ollama chat format
            # Ollama /api/chat expects: {"model": "...", "messages": [...], "stream": false}
            # Roles supported: system, assistant, user
            ollama_messages = []
            for msg in messages:
                role = msg.get("role", "user")
                # Map 'developer' role to 'system' (Ollama doesn't have developer role)
                if role == "developer":
                    role = "user"
                    content = f"[Instruction] {msg.get('content', '')}"
                else:
                    content = msg.get("content", "")
                ollama_messages.append({"role": role, "content": content})

            payload = {
                "model": self.model_name,
                "messages": ollama_messages,
                "stream": False,
                "options": {"temperature": self.temperature},
            }

            response = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=self.timeout,
            )
            response.raise_for_status()

            result = response.json()
            answer = result.get("message", {}).get("content", "").strip()

            if not answer:
                logger.warning("Ollama returned empty response")
                return "[No answer generated]"

            return answer

        except requests.Timeout:
            logger.error(f"Ollama request timed out after {self.timeout}s")
            raise RuntimeError(
                f"Ollama request timed out. Try increasing timeout or check Ollama service."
            )
        except requests.RequestException as e:
            logger.error(f"Ollama request failed: {e}")
            raise RuntimeError(f"Failed to call Ollama: {e}")
        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            raise

    def __call__(self, messages: List[dict], hits: Sequence[RetrievalHit]) -> str:
        """Make the generator callable for use with RAGService.query()."""
        return self.generate(messages, hits)


class SimpleContextGenerator:
    """Fallback generator that returns formatted context without LLM.
    
    Used when Ollama is not available or for testing.
    """

    def __init__(self):
        pass

    def is_available(self) -> bool:
        """Always available (no external dependency)."""
        return True

    def generate(self, messages: List[dict], hits: Sequence[RetrievalHit]) -> str:
        """Return formatted context hits as answer.
        
        Args:
            messages: Ignored
            hits: Retrieved context chunks
            
        Returns:
            Formatted context summary
        """
        if not hits:
            return "[No relevant context found]"

        lines = []
        for i, hit in enumerate(hits, start=1):
            chunk = hit.chunk
            lines.append(
                f"{i}. [{chunk.source}:{chunk.chunk_id}] (score: {hit.score:.2f})\n{chunk.text}"
            )
        return "\n\n".join(lines)

    def __call__(self, messages: List[dict], hits: Sequence[RetrievalHit]) -> str:
        """Make the generator callable for use with RAGService.query()."""
        return self.generate(messages, hits)


def get_default_generator(prefer_ollama: bool = True) -> OllamaGenerator | SimpleContextGenerator:
    """Get the best available generator.
    
    Args:
        prefer_ollama: If True, try Ollama first; if unavailable, fall back to context
        
    Returns:
        OllamaGenerator if available and preferred, else SimpleContextGenerator
    """
    if prefer_ollama:
        ollama_gen = OllamaGenerator()
        if ollama_gen.is_available():
            logger.info("Using Ollama generator")
            return ollama_gen
        logger.info("Ollama not available, falling back to context-only generator")
        return SimpleContextGenerator()
    else:
        return SimpleContextGenerator()
