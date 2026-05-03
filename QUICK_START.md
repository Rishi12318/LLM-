# 🚀 Quick Start: RAG + Ollama Integration

Your Multilingual Transcriber now has a **complete production-ready RAG system with Ollama integration** for LLM-based answer generation. This guide gets you up and running in 5 minutes.

## Prerequisites

- Python 3.9+
- Backend already set up (from previous setup)
- **Optional**: Ollama (for LLM generation; system works without it)

## 1️⃣ Install Dependencies (1 minute)

```bash
cd multilingual-transcriber
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r backend/requirements.txt
```

Key new packages:
- `requests` - for calling Ollama API
- `sentence-transformers` - for semantic embeddings
- `scikit-learn` - for TF-IDF fallback

## 2️⃣ Setup Ollama (Optional but Recommended, 3 minutes)

### Option A: Full LLM Generation (Recommended)

1. **Install Ollama**:
   - macOS: `brew install ollama`
   - Linux: `curl -fsSL https://ollama.ai/install.sh | sh`
   - Windows: Download from https://ollama.ai

2. **Pull a model**:
   ```bash
   ollama pull mistral
   # (~4GB, wait 2-3 minutes)
   ```

3. **Start Ollama**:
   ```bash
   ollama serve
   # Runs on http://localhost:11434
   # Keep this running in a separate terminal
   ```

### Option B: Context-Only Mode (No Ollama)

Skip the Ollama setup. The system automatically falls back to returning formatted context instead of LLM-generated answers. All features work the same.

## 3️⃣ Start the Backend (1 minute)

In a new terminal:
```bash
cd multilingual-transcriber
source .venv/bin/activate
python -m uvicorn backend.api:app --reload
```

Backend runs at: `http://localhost:8000`

## 4️⃣ Test Everything

### Option A: Run Full Example Script
```bash
python OLLAMA_EXAMPLE.py
```

This ingests sample documents and runs several RAG queries with and without LLM generation.

### Option B: Manual API Test

**Ingest a document**:
```bash
curl -X POST http://localhost:8000/rag/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "source_name": "Python Guide",
    "text": "Python is a programming language. It was created by Guido van Rossum. Python emphasizes readability.",
    "document_id": "python-101"
  }'
```

**Query with LLM (Ollama)**:
```bash
curl -X POST http://localhost:8000/rag/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Who created Python?",
    "top_k": 5,
    "use_llm": true
  }'
```

**Query without LLM (Context only)**:
```bash
curl -X POST http://localhost:8000/rag/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Who created Python?",
    "use_llm": false
  }'
```

**Response**:
```json
{
  "question": "Who created Python?",
  "answer": "Guido van Rossum created Python [source:python-101:chunk_0]. He emphasized readability [source:python-101:chunk_1].",
  "retrieval": [
    {
      "chunk_id": "python-101:chunk_0",
      "source": "Python Guide",
      "score": 0.95,
      "text": "Python was created by Guido van Rossum..."
    }
  ],
  "validation": {
    "is_grounded": true,
    "groundedness": 0.95,
    "citations": ["python-101:chunk_0"],
    "warnings": []
  }
}
```

## 5️⃣ Validate Everything Works

```bash
python RAG_VALIDATION.py
```

Expected output: **✅ All tests passed!**

## 📊 Architecture

```
User Request
    ↓
[API] POST /rag/ingest → Store documents
[API] POST /rag/query → Retrieve + Generate
    ↓
[RAGService] Retrieval
    ├─ Query embedding
    ├─ Vector search (FAISS or TF-IDF)
    └─ Return top-k chunks
    ↓
[OllamaGenerator or SimpleContextGenerator]
    ├─ Ollama: LLM-based answer with citations
    └─ Context: Formatted document excerpts
    ↓
[Validation Layer]
    ├─ Citation extraction
    ├─ Hallucination detection
    └─ Groundedness scoring
    ↓
Response to User
```

## 🎯 Key Features

✅ **Automatic fallback**: No Ollama? Get formatted context instead  
✅ **Citation tracking**: Answers include `[source:chunk_id]` references  
✅ **Hallucination detection**: Warns if answer goes beyond context  
✅ **Auto-indexing**: Transcripts are automatically indexed after processing  
✅ **Evaluation metrics**: Token F1, Jaccard, relevance, correctness, groundedness  
✅ **Multiple formats**: JSON, Markdown, SRT output formats  
✅ **Multi-language**: 100+ languages supported  

## 🔧 Common Tasks

### Use a Different Ollama Model
```python
# In api.py or your code:
rag_generator = OllamaGenerator(model_name="neural-chat")
```

Available models: `mistral`, `neural-chat`, `orca-mini`, `llama2`, `openchat`

### Disable Ollama
```python
# Force context-only mode:
from backend.rag import SimpleContextGenerator
rag_generator = SimpleContextGenerator()
```

### Query with Large Documents
```bash
curl -X POST http://localhost:8000/rag/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Your question here",
    "top_k": 10,
    "use_llm": true
  }'
```

### Check System Status
```bash
curl http://localhost:8000/health
```

Returns:
```json
{
  "status": "healthy",
  "device": "cuda" or "cpu",
  "rag_index": {
    "document_count": 5,
    "chunk_count": 42,
    "backend": "sentence-transformers" or "tfidf"
  }
}
```

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| `Connection refused` | Make sure `ollama serve` is running in another terminal |
| `Model not found` | Run `ollama pull mistral` (or your model name) |
| `Out of memory` | Use `ollama pull orca-mini` (smaller model) |
| `Slow responses` | Normal for first query (model loads). Subsequent queries are fast. |
| `No citations in answer` | Ollama may not follow citation format. This is OK—validation will flag it. |

## 📈 Next Steps

1. **Ingest more documents**: Use `/rag/ingest` endpoint
2. **Build a web UI**: The frontend already has placeholders for RAG results
3. **Evaluate quality**: Use `/rag/evaluate` to run metrics
4. **Deploy**: Use Docker/Kubernetes for production (see deployment guides)
5. **Monitor**: Check logs for hallucination warnings

## 📚 Full Documentation

- [README.md](README.md) - Project overview
- [OLLAMA_SETUP.md](OLLAMA_SETUP.md) - Detailed Ollama guide
- [backend/rag/](backend/rag/) - Source code documentation

## ✨ Example Workflow

```bash
# 1. Start services
ollama serve &                                    # Terminal 1
python -m uvicorn backend.api:app --reload &    # Terminal 2

# 2. Ingest documents
curl -X POST http://localhost:8000/rag/ingest \
  -H "Content-Type: application/json" \
  -d '{"source_name": "FAQ", "text": "Q: How does RAG work? A: It retrieves documents and generates grounded answers."}'

# 3. Query with LLM
curl -X POST http://localhost:8000/rag/query \
  -H "Content-Type: application/json" \
  -d '{"question": "How does RAG work?", "use_llm": true}'

# 4. Evaluate
curl -X POST http://localhost:8000/rag/evaluate
```

---

**🎉 You're ready! Start querying with LLM-powered answers backed by your own documents.**
