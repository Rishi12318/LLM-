"""
Example: Complete RAG + LLM Workflow with Ollama

This demonstrates the end-to-end flow:
1. Start transcription (outputs are auto-indexed)
2. Query the RAG system
3. Receive LLM-generated grounded answers with citations
"""

import requests
import json
from pathlib import Path

# Configuration
API_BASE = "http://localhost:8000"
EXAMPLE_DOCUMENTS = [
    {
        "source_name": "Python Basics",
        "text": """
        Python is a high-level, interpreted programming language. It was created by Guido van Rossum
        and first released in 1991. Python emphasizes code readability and simplicity, making it
        a popular choice for beginners and professionals alike.
        
        Key features of Python include:
        - Dynamic typing
        - Automatic memory management
        - Extensive standard library
        - Support for multiple programming paradigms (procedural, object-oriented, functional)
        
        Python is widely used in web development, data science, artificial intelligence,
        scientific computing, and automation.
        """,
        "document_id": "python-basics",
    },
    {
        "source_name": "Machine Learning Overview",
        "text": """
        Machine Learning (ML) is a subset of Artificial Intelligence that enables systems to learn
        and improve from experience without being explicitly programmed. ML algorithms identify
        patterns in data and make predictions or decisions based on those patterns.
        
        Types of Machine Learning:
        1. Supervised Learning: Learning from labeled data (e.g., classification, regression)
        2. Unsupervised Learning: Finding patterns in unlabeled data (e.g., clustering)
        3. Reinforcement Learning: Learning through trial and error with rewards
        
        Common ML algorithms include Decision Trees, Random Forests, Support Vector Machines,
        Neural Networks, and K-Means Clustering. ML is used in recommendation systems,
        image recognition, natural language processing, and predictive analytics.
        """,
        "document_id": "ml-overview",
    },
]


def ingest_documents():
    """Ingest example documents into the RAG system."""
    print("📚 Ingesting documents into RAG system...")
    for doc in EXAMPLE_DOCUMENTS:
        response = requests.post(
            f"{API_BASE}/rag/ingest",
            json={
                "source_name": doc["source_name"],
                "text": doc["text"],
                "document_id": doc["document_id"],
                "metadata": {"type": "example", "ingestion_type": "demo"},
            },
        )
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ Ingested: {doc['source_name']}")
            print(f"     Index stats: {data['index']}")
        else:
            print(f"  ❌ Failed to ingest {doc['source_name']}: {response.text}")


def query_with_llm(question: str, use_llm: bool = True):
    """Query the RAG system with optional LLM generation."""
    mode = "LLM-based" if use_llm else "context-only"
    print(f"\n🔍 Querying RAG system ({mode})...")
    print(f"   Question: {question}\n")

    response = requests.post(
        f"{API_BASE}/rag/query",
        json={"question": question, "top_k": 5, "use_llm": use_llm},
    )

    if response.status_code == 200:
        result = response.json()

        print("📊 Retrieval Results:")
        print(f"   Retrieved {len(result['retrieval'])} chunks\n")

        for i, hit in enumerate(result["retrieval"], 1):
            print(f"   [{i}] {hit['source']}:{hit['chunk_id']} (score: {hit['score']:.2f})")
            print(f"       {hit['text'][:100]}...\n")

        print("💡 Generated Answer:")
        print(f"   {result['answer']}\n")

        print("✓ Validation Results:")
        val = result["validation"]
        print(f"   - Grounded: {val['is_grounded']}")
        print(f"   - Groundedness Score: {val['groundedness_score']:.2f}")
        print(f"   - Unsupported Ratio: {val['unsupported_ratio']:.2f}")
        print(f"   - Citations: {val['citations']}")
        if val["warnings"]:
            print(f"   - Warnings: {', '.join(val['warnings'])}")

        return result
    else:
        print(f"❌ Query failed: {response.text}")
        return None


def evaluate_rag():
    """Run the evaluation suite."""
    print("\n📈 Running RAG Evaluation Suite...\n")
    response = requests.post(f"{API_BASE}/rag/evaluate")

    if response.status_code == 200:
        result = response.json()
        print("Evaluation Results:")
        print(json.dumps(result, indent=2))
        return result
    else:
        print(f"❌ Evaluation failed: {response.text}")
        return None


def check_status():
    """Check API health and RAG index status."""
    print("🏥 Checking API Status...\n")
    response = requests.get(f"{API_BASE}/health")

    if response.status_code == 200:
        health = response.json()
        print(f"Status: {health['status']}")
        print(f"Device: {health['device']}")
        rag_stats = health.get("rag_index", {})
        print(f"RAG Index: {rag_stats.get('documents', 0)} docs, "
              f"{rag_stats.get('chunks', 0)} chunks, "
              f"backend: {rag_stats.get('embedding_backend', 'unknown')}")
        return health
    else:
        print(f"❌ Health check failed: {response.text}")
        return None


def main():
    """Run the complete example workflow."""
    print("=" * 70)
    print("🚀 MULTILINGUAL TRANSCRIBER - RAG + OLLAMA EXAMPLE")
    print("=" * 70)
    print()
    print("Prerequisites:")
    print("  1. Backend API running: python -m uvicorn backend.api:app --reload")
    print("  2. (Optional) Ollama running: ollama serve")
    print("     - Pull a model first: ollama pull mistral")
    print()

    # Check health
    if not check_status():
        print("\n⚠️  Backend API is not running. Start it with:")
        print("   python -m uvicorn backend.api:app --reload")
        return

    # Ingest documents
    ingest_documents()

    # Example queries
    questions = [
        "What is Python and what are its key features?",
        "Explain machine learning and its types.",
        "What is the relationship between Python and machine learning?",
    ]

    print("\n" + "=" * 70)
    print("QUERYING WITH LLM (OLLAMA)")
    print("=" * 70)

    for question in questions:
        query_with_llm(question, use_llm=True)
        print("-" * 70)

    # Fallback example
    print("\n" + "=" * 70)
    print("QUERYING WITHOUT LLM (CONTEXT-ONLY FALLBACK)")
    print("=" * 70)
    query_with_llm(questions[0], use_llm=False)

    # Evaluate
    print("\n" + "=" * 70)
    print("EVALUATION METRICS")
    print("=" * 70)
    evaluate_rag()

    print("\n" + "=" * 70)
    print("✅ Example Complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
