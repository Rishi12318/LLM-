# Ollama + RAG Setup Guide

This guide will help you set up Ollama for LLM-based answer generation with the Multilingual Transcriber's RAG system.

## What is Ollama?

[Ollama](https://ollama.ai) is a tool that lets you run large language models locally on your machine. It's perfect for:
- 🔒 Privacy (no data sent to external APIs)
- ⚡ Speed (low latency, no network dependency)
- 💰 Cost (free, no API charges)
- 🎮 Local experimentation

## Installation

### macOS
```bash
brew install ollama
# Then start the server
ollama serve
```

### Linux
```bash
curl -fsSL https://ollama.ai/install.sh | sh
# Then start the server
ollama serve
```

### Windows
1. Download the installer from https://ollama.ai/download
2. Run the installer
3. Ollama will start automatically as a background service
4. Or manually start: `ollama serve`

## Choosing a Model

Different models have different trade-offs:

| Model | Size | Speed | Quality | Best For |
|-------|------|-------|---------|----------|
| **mistral** | 7B | Fast | Good | 🏆 Recommended for RAG |
| **neural-chat** | 7B | Fast | Very Good | Conversational QA |
| **orca-mini** | 3B | Very Fast | Fair | Low-resource machines |
| **llama2** | 7B-70B | Variable | Very Good | General purpose |
| **openchat** | 7B | Fast | Good | Fast inference |

### For RAG (Recommended)
```bash
ollama pull mistral
```

### For Limited Resources
```bash
ollama pull orca-mini
```

### For Higher Quality
```bash
ollama pull neural-chat
```

## Quick Start

### 1. Install Ollama
Follow the installation steps above for your OS.

### 2. Pull a Model
```bash
ollama pull mistral
# This downloads ~4GB, takes a few minutes on first run
```

### 3. Start Ollama Server
```bash
ollama serve
# Should print: "Listening on 127.0.0.1:11434"
```

### 4. Start the Multilingual Transcriber Backend
In a new terminal:
```bash
cd /path/to/multilingual-transcriber
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
python -m uvicorn backend.api:app --reload
```

### 5. Query the RAG System
```bash
curl -X POST http://localhost:8000/rag/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the document about?",
    "use_llm": true
  }'
```

## Troubleshooting

### Ollama Connection Refused
```
Error: Failed to call Ollama: Connection refused
```
**Solution**: Make sure Ollama server is running:
```bash
ollama serve
```

### Model Not Found
```
Error: Ollama model 'mistral' not available
```
**Solution**: Pull the model:
```bash
ollama pull mistral
```

### Out of Memory
```
Error: out of memory / CUDA out of memory
```
**Solutions**:
1. Use a smaller model: `ollama pull orca-mini`
2. Reduce context window in generator.py (advanced)
3. Close other applications

### Timeout
```
Error: Ollama request timed out
```
**Solutions**:
1. Give Ollama more time to generate: Update timeout in api.py
2. Use a faster model (orca-mini instead of mistral)
3. Check system performance

## Configuration

### Change Ollama Port
By default, Ollama uses port 11434. To change it:

**macOS/Linux**:
```bash
OLLAMA_HOST=0.0.0.0:9999 ollama serve
```

**Windows**:
Set environment variable `OLLAMA_HOST=0.0.0.0:9999` and restart Ollama.

Then update api.py:
```python
rag_generator = OllamaGenerator(
    model_name="mistral",
    base_url="http://localhost:9999",  # Your custom port
)
```

### Adjust Temperature (Creativity)
Temperature controls randomness (0.0 = deterministic, 1.0 = very random):

```python
rag_generator = OllamaGenerator(
    model_name="mistral",
    temperature=0.3,  # Lower = more factual (good for RAG)
)
```

## System Requirements

### Minimum (with model quantization)
- 4GB RAM
- CPU with 2 cores
- Model: orca-mini

### Recommended
- 8GB RAM
- CPU with 4+ cores
- GPU optional but helpful
- Model: mistral

### Ideal
- 16GB RAM
- GPU with 6GB+ VRAM
- Model: mistral or neural-chat

## Automatic Fallback

If Ollama is not available:
1. Backend detects this during startup
2. Automatically switches to `SimpleContextGenerator`
3. User gets formatted context instead of LLM answer
4. **No errors or failures** — system still works!

You can control this behavior:
```python
# Force LLM (fails if Ollama unavailable)
rag_generator = OllamaGenerator()

# Prefer LLM, fallback to context
rag_generator = get_default_generator(prefer_ollama=True)
```

## Example Workflow

### 1. Ingest a Document
```bash
curl -X POST http://localhost:8000/rag/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "source_name": "My Document",
    "text": "Document content here...",
    "document_id": "doc-001"
  }'
```

### 2. Query with LLM
```bash
curl -X POST http://localhost:8000/rag/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is this document about?",
    "top_k": 5,
    "use_llm": true
  }'
```

### 3. Response with Citations
```json
{
  "question": "What is this document about?",
  "answer": "This document is about [source:chunk_0]. It covers [source:chunk_2]...",
  "retrieval": [
    {
      "chunk_id": "chunk_0",
      "source": "My Document",
      "score": 0.92,
      "text": "..."
    }
  ],
  "validation": {
    "is_grounded": true,
    "groundedness_score": 0.95,
    "citations": ["chunk_0", "chunk_2"],
    "warnings": []
  }
}
```

## Performance Tips

1. **Warm up the model**: First query takes longer (model loads into memory)
2. **Batch queries**: Multiple queries are faster than single queries
3. **Use GPU**: If available, Ollama automatically uses GPU
4. **Reduce context**: Smaller context windows = faster responses
5. **Quantized models**: Use 4-bit or 8-bit quantized models for speed

## Running Ollama in Production

For production deployments:

1. **Use systemd (Linux)**:
```bash
sudo systemctl start ollama
sudo systemctl enable ollama
```

2. **Use screen or tmux (Linux/macOS)**:
```bash
screen -S ollama ollama serve
# Detach with Ctrl+A, D
```

3. **Use Docker**:
```bash
docker run -d --gpus=all -p 11434:11434 ollama/ollama
```

4. **Windows Service**:
Use Task Scheduler or NSSM to run ollama.exe as a service

## Further Reading

- [Ollama Documentation](https://github.com/ollama/ollama)
- [Available Models](https://ollama.ai/library)
- [Model Performance Comparison](https://huggingface.co/spaces/HuggingFaceH4/open_llm_leaderboard)
- [Prompt Engineering Guide](https://platform.openai.com/docs/guides/prompt-engineering)

## Support

Issues or questions?
1. Check [Ollama GitHub Issues](https://github.com/ollama/ollama/issues)
2. Review the [RAG documentation](README.md#-production-upgrade)
3. Run OLLAMA_DEBUG=1 ollama serve for debug output

---

**Happy RAG querying! 🚀**
