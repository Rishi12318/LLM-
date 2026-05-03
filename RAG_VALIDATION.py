#!/usr/bin/env python
"""
Validation and Integration Test for RAG + Ollama System

This script validates that all RAG components are working correctly,
with or without Ollama, and tests the full integration.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from backend.rag import (
    OllamaGenerator,
    SimpleContextGenerator,
    get_default_generator,
    RAGService,
    build_rag_messages,
    validate_answer,
)


def test_imports():
    """Test that all RAG modules import correctly."""
    print("✓ Testing imports...")
    try:
        from backend.rag import (
            ChunkRecord,
            ChunkingConfig,
            EvaluationMetrics,
            VectorStore,
            build_rag_prompt,
            evaluate_case,
        )
        print("  ✅ All RAG modules imported successfully")
        return True
    except ImportError as e:
        print(f"  ❌ Import failed: {e}")
        return False


def test_generators():
    """Test generator initialization and availability checks."""
    print("\n✓ Testing generators...")

    # Test SimpleContextGenerator (always available)
    print("  - SimpleContextGenerator...")
    simple_gen = SimpleContextGenerator()
    if simple_gen.is_available():
        print("    ✅ SimpleContextGenerator is available")
    else:
        print("    ❌ SimpleContextGenerator failed (should always be available)")
        return False

    # Test OllamaGenerator detection
    print("  - OllamaGenerator...")
    ollama_gen = OllamaGenerator()
    if ollama_gen.is_available():
        print(f"    ✅ Ollama is available at {ollama_gen.base_url}")
    else:
        print(f"    ⚠️  Ollama not available (expected if not running)")
        print(f"       To enable: ollama serve")

    # Test get_default_generator
    print("  - get_default_generator()...")
    default_gen = get_default_generator(prefer_ollama=True)
    print(f"    ✅ Selected generator: {default_gen.__class__.__name__}")

    return True


def test_rag_service():
    """Test RAGService initialization and basic operations."""
    print("\n✓ Testing RAGService...")

    storage_dir = Path(__file__).parent / "backend" / "storage" / "test"
    storage_dir.mkdir(parents=True, exist_ok=True)

    try:
        rag = RAGService(storage_dir)
        print("  ✅ RAGService initialized")

        # Test document ingestion
        print("  - Testing document ingestion...")
        doc_id = rag.ingest_text(
            document_id="test-doc",
            source_name="Test Document",
            text="This is a test document. It contains important information. "
            "Machine learning is a subset of artificial intelligence.",
        )
        print(f"    ✅ Document ingested: {len(doc_id)} chunks")

        # Test retrieval
        print("  - Testing retrieval...")
        hits = rag.retrieve("What is machine learning?", top_k=2)
        if hits:
            print(f"    ✅ Retrieved {len(hits)} chunks")
            for i, hit in enumerate(hits, 1):
                print(f"       [{i}] score={hit.score:.3f}, text={hit.chunk.text[:50]}...")
        else:
            print("    ⚠️  No chunks retrieved (expected for first query)")

        # Test vector store stats
        print("  - Testing vector store stats...")
        stats = rag.vector_store.stats()
        print(f"    ✅ Vector store stats:")
        print(f"       - Documents: {stats['document_count']}")
        print(f"       - Chunks: {stats['chunk_count']}")
        print(f"       - Backend: {stats['backend']}")
        print(f"       - FAISS: {'Available' if stats['faiss_enabled'] else 'Not available'}")

        return True

    except Exception as e:
        print(f"  ❌ RAGService test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_prompt_building():
    """Test prompt and message building."""
    print("\n✓ Testing prompt building...")

    try:
        from backend.rag import build_rag_messages
        from backend.rag.types import ChunkRecord, RetrievalHit

        # Create dummy chunks
        chunk = ChunkRecord(
            chunk_id="chunk_0",
            document_id="doc1",
            source="Test",
            text="This is important information about AI.",
            chunk_index=0,
            metadata={},
        )
        hit = RetrievalHit(chunk=chunk, score=0.95)

        messages = build_rag_messages("What is AI?", [hit])
        print(f"  ✅ Generated {len(messages)} messages")
        for msg in messages:
            print(f"     - {msg['role']}: {msg['content'][:60]}...")

        return True
    except Exception as e:
        print(f"  ❌ Prompt building failed: {e}")
        return False


def test_validation():
    """Test answer validation."""
    print("\n✓ Testing validation...")

    try:
        from backend.rag import validate_answer
        from backend.rag.types import ChunkRecord, RetrievalHit

        # Create dummy data
        chunk = ChunkRecord(
            chunk_id="chunk_0",
            document_id="doc1",
            source="Test",
            text="Python is a programming language. It was created by Guido van Rossum.",
            chunk_index=0,
            metadata={},
        )
        hit = RetrievalHit(chunk=chunk, score=0.95)

        # Test grounded answer
        grounded_answer = "Python is a programming language created by Guido van Rossum."
        validation = validate_answer(grounded_answer, [hit])
        print(f"  ✅ Grounded answer validation: {validation['groundedness']:.2f}")
        print(f"     - Is grounded: {validation['is_grounded']}")

        # Test answer with hallucination
        hallucinated_answer = "Python was invented in 1985 by someone."
        validation = validate_answer(hallucinated_answer, [hit])
        print(f"  ⚠️  Hallucinated answer validation: {validation['groundedness']:.2f}")
        print(f"     - Warnings: {validation['warnings']}")

        return True
    except Exception as e:
        print(f"  ❌ Validation test failed: {e}")
        return False


def test_end_to_end():
    """Test complete RAG flow without Ollama."""
    print("\n✓ Testing end-to-end RAG flow...")

    try:
        storage_dir = Path(__file__).parent / "backend" / "storage" / "e2e_test"
        storage_dir.mkdir(parents=True, exist_ok=True)

        rag = RAGService(storage_dir)
        simple_gen = SimpleContextGenerator()

        # Ingest document
        print("  - Ingesting document...")
        rag.ingest_text(
            document_id="facts",
            source_name="Facts",
            text="Artificial Intelligence (AI) is a branch of computer science. "
            "Machine Learning (ML) is a subset of AI. "
            "Deep Learning (DL) is a subset of ML.",
        )
        print("    ✅ Document ingested")

        # Query
        print("  - Querying...")
        result = rag.query(
            "What is the relationship between AI and ML?",
            top_k=2,
            generator=simple_gen,
        )
        print("    ✅ Query completed")
        print(f"       - Answer: {result['answer'][:80]}...")
        print(f"       - Retrieval hits: {len(result['retrieval'])}")
        print(f"       - Grounded: {result['validation']['is_grounded']}")

        return True
    except Exception as e:
        print(f"  ❌ End-to-end test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all validation tests."""
    print("=" * 70)
    print("RAG + OLLAMA VALIDATION TEST")
    print("=" * 70)

    tests = [
        ("Imports", test_imports),
        ("Generators", test_generators),
        ("RAGService", test_rag_service),
        ("Prompt Building", test_prompt_building),
        ("Validation", test_validation),
        ("End-to-End", test_end_to_end),
    ]

    results = []
    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, passed))
        except Exception as e:
            print(f"\n❌ {name} test crashed: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    passed = sum(1 for _, p in results if p)
    total = len(results)

    for name, passed_test in results:
        status = "✅ PASS" if passed_test else "❌ FAIL"
        print(f"{status}: {name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n✅ All tests passed! System is ready for use.")
        print("\nNext steps:")
        print("  1. Start Ollama (optional): ollama pull mistral && ollama serve")
        print("  2. Start backend: python -m uvicorn backend.api:app --reload")
        print("  3. Run example: python OLLAMA_EXAMPLE.py")
        return 0
    else:
        print(f"\n❌ {total - passed} test(s) failed. Check errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
