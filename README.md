# 🎙️ Multilingual Audio Transcriber & Translator

<div align="center">

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Whisper](https://img.shields.io/badge/Whisper-Large%20V3-green.svg)](https://github.com/openai/whisper)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-009688.svg)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-16.1-black.svg)](https://nextjs.org/)

**A professional-grade, fully offline audio transcription system with speaker diarization, translation, and a modern web interface.**

[Features](#-features) • [Quick Start](#-quick-start) • [Installation](#-installation) • [Usage](#-usage) • [API](#-api-reference) • [Documentation](#-documentation)

</div>

---

## 📖 Overview

Multilingual Audio Transcriber is a complete end-to-end solution for transcribing, analyzing, and translating audio content. It combines state-of-the-art AI models for speech recognition, speaker identification, and translation—all running 100% offline after initial setup.

### Why This Project?

- ✅ **No API Keys Required** - All models run locally
- ✅ **Complete Privacy** - Your audio never leaves your machine
- ✅ **Production Ready** - Includes both CLI and web interface
- ✅ **Industry Standard Models** - Whisper Large V3, Pyannote 3.1
- ✅ **Multi-Format Support** - JSON, Markdown, SRT, Plain Text
- ✅ **Enterprise Features** - Speaker diarization, timestamps, confidence scores

---

## ✨ Features

### Core Capabilities

| Feature | Description |
|---------|-------------|
| 🌍 **100+ Languages** | Automatic language detection with Whisper Large V3 |
| 👥 **Speaker Diarization** | Identifies who spoke when using Pyannote 3.1 |
| 🔄 **Auto-Translation** | Translates to English using Helsinki-NLP OPUS-MT models |
| 📄 **Multiple Output Formats** | JSON, Markdown, SRT subtitles, and plain text |
| 🚀 **100% Offline** | All models cached locally, no internet needed after setup |
| 🖥️ **GPU/CPU Support** | Auto-detects CUDA, MPS (Apple Silicon), or CPU |
| 🎵 **Universal Audio Support** | WAV, MP3, M4A, FLAC, OGG, and more via FFmpeg |
| 🌐 **Modern Web UI** | Beautiful Next.js frontend with real-time progress |
| 🔌 **REST API** | FastAPI backend for integration with other services |

### Interface Options

1. **Web Interface** (Recommended)
   - Drag-and-drop file upload
   - Real-time progress tracking
   - Download results in any format
   - Modern, responsive design

2. **Command Line Interface**
   - Rich terminal output
   - Progress bars and status updates
   - Batch processing support
   - Scriptable for automation

3. **REST API**
   - FastAPI with automatic documentation
   - Async job processing
   - Status polling endpoints
   - Easy integration

---

## 🚀 Quick Start

### Option 1: Web Interface (Easiest)

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/multilingual-transcriber.git
cd multilingual-transcriber

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Start the backend
cd backend
python api.py

# 4. In a new terminal, start the frontend
cd frontend
npm install
npm run dev

# 5. Open http://localhost:3000 in your browser
```

### Option 2: Command Line

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run transcription
python main.py your_audio.wav

# Done! Results saved to output/ directory
```

---

## 💻 Installation

### Prerequisites

- **Python 3.9 or higher**
- **Node.js 18+ and npm** (for web interface only)
- **FFmpeg** (for audio format support)

### Step 1: Install FFmpeg

<details>
<summary><strong>Windows</strong></summary>

Using Chocolatey:
```bash
choco install ffmpeg
```

Or manual installation:
1. Download from [ffmpeg.org](https://ffmpeg.org/download.html)
2. Extract to `C:\ffmpeg`
3. Add `C:\ffmpeg\bin` to System PATH
4. Restart terminal

</details>

<details>
<summary><strong>macOS</strong></summary>

```bash
brew install ffmpeg
```

</details>

<details>
<summary><strong>Linux (Ubuntu/Debian)</strong></summary>

```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

</details>

### Step 2: Install Python Dependencies

```bash
# Navigate to project directory
cd multilingual-transcriber

# Create virtual environment (recommended)
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: (Optional) Setup HuggingFace for Speaker Diarization

Speaker diarization requires accepting Pyannote model terms:

1. Create account at [huggingface.co](https://huggingface.co)
2. Accept terms at [pyannote/speaker-diarization-3.1](https://huggingface.co/pyannote/speaker-diarization-3.1)
3. Create access token at [Settings > Access Tokens](https://huggingface.co/settings/tokens)
4. Login via CLI:
   ```bash
   huggingface-cli login
   ```

**Alternative:** Skip diarization with `--skip-diarization` flag

### Step 4: (Optional) Install Frontend

```bash
cd frontend
npm install
```

### Verification

```bash
# Test installation
python main.py test

# Should display:
# ✓ Python 3.9+
# ✓ PyTorch
# ✓ FFmpeg
# ✓ All dependencies installed
```

---

## 🎯 Usage

### Web Interface

1. **Start Backend Server**
   ```bash
   cd backend
   python api.py
   # Backend running at http://127.0.0.1:8000
   ```

2. **Start Frontend (New Terminal)**
   ```bash
   cd frontend
   npm run dev
   # Frontend running at http://localhost:3000
   ```

3. **Open Browser**
   - Navigate to `http://localhost:3000`
   - Upload audio file (drag-and-drop or browse)
   - Wait for processing
   - Download results in your preferred format

### Command Line Interface

#### Basic Usage

```bash
# Transcribe an audio file
python main.py audio.wav

# Use specific Whisper model
python main.py audio.mp3 --model medium

# Force GPU or CPU
python main.py audio.wav --device cuda
python main.py audio.wav --device cpu

# Skip speaker diarization (faster)
✓ Aligned 12 segments with 2 speaker(s)

🔄 STEP 5: TRANSLATION
Translating Hindi → English
✓ Translated 12 segments

📄 STEP 6: SAVING OUTPUTS
✓ Saved JSON: output/2025-12-30_125430/result.json
✓ Saved Markdown: output/2025-12-30_125430/result.md
✓ Saved text: output/2025-12-30_125430/result.txt
✓ Saved SRT: output/2025-12-30_125430/result_original.srt
✓ Saved SRT: output/2025-12-30_125430/result_english.srt

✅ PROCESSING COMPLETE
Duration: 45s | Speakers: 2 | Processing Time: 1m 35s
```

## 📄 Output Formats

### Markdown Example

```markdown
# Audio Transcription & Translation

**Language:** Hindi (hi) | **Speakers:** 2 | **Duration:** 00:45

---

## Speaker 1

**[00:01-00:05]** नमस्ते, आप कैसे हैं?  
**EN:** Hello, how are you?

**[00:12-00:18]** मैं ठीक हूँ, धन्यवाद। आपका दिन कैसा रहा?  
**EN:** I'm fine, thank you. How was your day?

## Speaker 2  

**[00:06-00:11]** मैं भी ठीक हूँ। आपसे मिलकर अच्छा लगा।  
**EN:** I'm also fine. Nice to meet you.
```

### JSON Example

```json
{
  "metadata": {
    "language": "hi",
    "speakers": 2,
    "duration": 45.2,
    "total_segments": 12,
    "timestamp": "2025-12-30T12:54:30"
  },
  "segments": [
    {
      "speaker": "Speaker 1",
      "start": 1.2,
      "end": 5.4,
      "original": "नमस्ते, आप कैसे हैं?",
      "english": "Hello, how are you?",
      "lang": "hi"
    }
  ]
}
```

## 🎯 Command-Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `audio_file` | Path to audio file (required) | - |
| `--output-dir`, `-o` | Output directory | `./output` |
| `--model`, `-m` | Whisper model size | `large-v3` |
| `--device`, `-d` | Device (cuda/cpu/mps/auto) | `auto` |
| `--skip-diarization` | Skip speaker separation | `False` |
| `--min-speakers` | Minimum speakers | `1` |
| `--max-speakers` | Maximum speakers | `auto` |

### Whisper Model Sizes

| `tiny` | ~75MB | Fastest | Low |
| `base` | ~150MB | Very Fast | Medium |
| `small` | ~500MB | Fast | Good |
| `medium` | ~1.5GB | Moderate | Very Good |
| `large-v3` | ~3GB | Slower | Excellent |

**Recommendation:** Use `large-v3` for best accuracy, `medium` for balanced performance.

---

## 🌐 Supported Languages

**100+ languages supported** including:

### Major Languages
Arabic, Chinese, Czech, Danish, Dutch, English, Estonian, Finnish, French, German, Greek, Hebrew, Hindi, Hungarian, Indonesian, Italian, Japanese, Korean, Latvian, Lithuanian, Malay, Norwegian, Polish, Portuguese, Romanian, Russian, Slovak, Spanish, Swedish, Tamil, Telugu, Thai, Turkish, Ukrainian, Urdu, Vietnamese

### Additional Regional Languages
Bengali, Gujarati, Kannada, Malayalam, Marathi, Punjabi, Sinhala, and many more

**Auto-detection:** The system automatically detects the language—no manual selection needed!

---

## 📁 Project Architecture

```
multilingual-transcriber/
├── 📄 main.py                    # CLI entrypoint (Typer)
├── 📦 requirements.txt           # Python dependencies
├── 📋 pyproject.toml            # Poetry configuration
├── 📖 README.md                 # This file
├── 📝 SETUP.md                  # Quick setup guide
├── 📚 USAGE.md                  # Detailed usage guide
├── 📊 PROJECT_SUMMARY.md        # Project overview
│
├── 📂 backend/                   # FastAPI REST API
│   ├── api.py                   # API endpoints
│   ├── requirements.txt         # Backend dependencies
│   ├── uploads/                 # Temporary file uploads
│   └── results/                 # Generated transcriptions
│
├── 📂 frontend/                  # Next.js web interface
│   ├── app/                     # App router (Next.js 13+)
│   │   ├── layout.tsx          # Root layout
│   │   ├── page.tsx            # Home page
│   │   └── globals.css         # Global styles
│   ├── components/              # React components
│   │   ├── AudioUploader.tsx   # File upload component
│   │   └── TranscriptionResults.tsx  # Results display
│   ├── package.json            # Node dependencies
│   └── next.config.ts          # Next.js config
│
├── 📂 pipeline/                  # Audio processing pipeline
│   ├── __init__.py             # Package exports
│   ├── audio_loader.py         # Audio file loading
│   ├── whisper_asr.py          # Whisper transcription
│   ├── pyannote_diar.py        # Speaker diarization
│   ├── align_segments.py       # Speaker-text alignment
│   ├── translate.py            # Text translation
│   └── format_output.py        # Output generation
│
├── 📂 models/                    # Model management
│   ├── __init__.py             # Package exports
│   ├── config.py               # Model configurations
│   └── cache_manager.py        # Auto-download & caching
│
└── 📂 utils/                     # Utility functions
    ├── __init__.py             # Package exports
    └── helpers.py              # Helper functions
```

---

## 🔌 API Documentation

### Starting the Backend

```bash
cd backend
python api.py
```

Server runs at: **http://127.0.0.1:8000**

### Interactive Docs

- **Swagger UI:** http://127.0.0.1:8000/docs
- **ReDoc:** http://127.0.0.1:8000/redoc

### API Endpoints

#### 1. Health Check

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "device": "cuda",
  "timestamp": "2026-01-03T10:30:00"
}
```

#### 2. Transcribe Audio

```http
POST /transcribe
Content-Type: multipart/form-data

Parameters:
  - file: audio file (WAV, MP3, M4A, etc.)
  - model: whisper model (default: "large-v3")
  - skip_diarization: boolean (default: true)
```

**Example (cURL):**
```bash
curl -X POST "http://127.0.0.1:8000/transcribe" \
  -F "file=@audio.mp3" \
  -F "model=large-v3" \
  -F "skip_diarization=true"
```

**Response:**
```json
{
  "job_id": "20251230_194808",
  "status": "processing",
  "message": "Job queued for processing"
}
```

#### 3. Check Job Status

```http
GET /status/{job_id}
```

**Response:**
```json
{
  "job_id": "20251230_194808",
  "status": "completed",
  "progress": 100,
  "message": "Transcription complete",
  "result": {
    "metadata": {
      "language": "en",
      "duration": 120.5
    },
    "segments": [...]
  }
}
```

#### 4. Download Results

```http
GET /download/{job_id}/{format}
```

**Formats:** `json`, `md`, `txt`, `srt_original`, `srt_english`

**Example:**
```bash
curl "http://127.0.0.1:8000/download/20251230_194808/json" -o result.json
```

### Python SDK Example

```python
import requests
import time

BASE_URL = "http://127.0.0.1:8000"

# Upload audio
with open("audio.mp3", "rb") as f:
    response = requests.post(
        f"{BASE_URL}/transcribe",
        files={"file": f},
        data={"model": "large-v3", "skip_diarization": "true"}
    )

job_id = response.json()["job_id"]
print(f"Job ID: {job_id}")

# Poll for completion
while True:
    status_response = requests.get(f"{BASE_URL}/status/{job_id}")
    status_data = status_response.json()
    
    print(f"Status: {status_data['status']} ({status_data['progress']}%)")
    
    if status_data["status"] == "completed":
        result = status_data["result"]
        break
    elif status_data["status"] == "failed":
        print(f"Error: {status_data['message']}")
        break
    
    time.sleep(5)

# Download JSON
json_response = requests.get(f"{BASE_URL}/download/{job_id}/json")
with open("result.json", "wb") as f:
    f.write(json_response.content)

print("✓ Results downloaded")
```

---

## 🚀 Deployment

### Running in Production

#### Option 1: Systemd Service (Linux)

Create `/etc/systemd/system/transcriber-api.service`:

```ini
[Unit]
Description=Multilingual Transcriber API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/multilingual-transcriber/backend
Environment="PATH=/opt/multilingual-transcriber/.venv/bin"
ExecStart=/opt/multilingual-transcriber/.venv/bin/python api.py

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable transcriber-api
sudo systemctl start transcriber-api
```

#### Option 2: Docker (Coming Soon)

```bash
# Build
docker build -t multilingual-transcriber .

# Run
docker run -p 8000:8000 -p 3000:3000 multilingual-transcriber
```

### Nginx Reverse Proxy

```nginx
server {
    listen 80;
    server_name transcribe.example.com;

    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
    }
}
```

---

## 🔧 Advanced Configuration

### Environment Variables

```bash
# Set HuggingFace cache directory
export HF_HOME=/path/to/cache

# Disable progress bars
export TRANSFORMERS_NO_PROGRESS=1

# Set PyTorch threads
export OMP_NUM_THREADS=8

# Enable verbose logging
export LOG_LEVEL=DEBUG
```

### Custom Model Paths

Edit [models/config.py](multilingual-transcriber/models/config.py):

```python
# Use custom Whisper model
WHISPER_MODELS = {
    "custom": "/path/to/custom/whisper/model"
}
```

### Performance Tuning

```bash
# GPU Memory optimization
python main.py audio.wav --model medium --device cuda

# Multi-threading (CPU)
export OMP_NUM_THREADS=$(nproc)

# Batch processing
for file in *.mp3; do
    python main.py "$file" --skip-diarization &
done
wait
```

---

## 🐛 Troubleshooting

### Common Issues

#### 1. FFmpeg Not Found

**Error:** `FFmpeg not found in PATH`

**Solution:**
- Install FFmpeg (see [Installation](#step-1-install-ffmpeg))
- Verify: `ffmpeg -version`
- Restart terminal

#### 2. CUDA Out of Memory

**Error:** `RuntimeError: CUDA out of memory`

**Solutions:**
```bash
# Use smaller model
python main.py audio.wav --model medium

# Use CPU
python main.py audio.wav --device cpu

# Reduce batch size (for developers)
# Edit whisper_asr.py: batch_size=8
```

#### 3. Pyannote Authentication

**Error:** `Access denied to pyannote/speaker-diarization-3.1`

**Solution:**
1. Visit https://huggingface.co/pyannote/speaker-diarization-3.1
2. Accept model conditions
3. Run: `huggingface-cli login`
4. Or use: `--skip-diarization`

#### 4. Slow CPU Performance

**Expected Times:**
- CPU: ~3-5 minutes per 1 minute of audio
- GPU: ~30 seconds per 1 minute of audio

**Tips:**
- Use `--model medium` or `--model small`
- Skip diarization: `--skip-diarization`
- Use GPU if available

#### 5. Port Already in Use

**Backend (8000):**
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/macOS
lsof -ti:8000 | xargs kill -9
```

**Frontend (3000):**
```bash
# Kill process on port 3000
npx kill-port 3000
```

### Debug Mode

```bash
# Enable detailed logging
python main.py audio.wav --verbose

# Check system
python main.py test

# View model info
python main.py info
```

---

## 🤝 Contributing

Contributions are welcome! Here's how:

### Development Setup

```bash
# Fork & clone
git clone https://github.com/yourusername/multilingual-transcriber.git
cd multilingual-transcriber

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install pre-commit hooks (optional)
pip install pre-commit
pre-commit install
```

### Making Changes

1. Create branch: `git checkout -b feature/your-feature`
2. Make changes
3. Test: `python main.py test`
4. Commit: `git commit -m "Add feature"`
5. Push: `git push origin feature/your-feature`
6. Open Pull Request

### Code Style

- Follow PEP 8
- Add type hints
- Write docstrings
- Update tests

---

## 📊 Performance Benchmarks

| Audio Length | Model | Device | Time | Notes |
|--------------|-------|--------|------|-------|
| 1 min | large-v3 | RTX 3080 | 30s | With diarization |
| 1 min | large-v3 | CPU (i7) | 3m | With diarization |
| 10 min | large-v3 | RTX 3080 | 4m | With diarization |
| 10 min | medium | RTX 3080 | 2m | With diarization |
| 60 min | large-v3 | RTX 3080 | 20m | With diarization |

*Hardware: RTX 3080, Intel i7-12700K, 32GB RAM*

---

## 🗺️ Roadmap

### Planned Features

- [ ] Real-time streaming transcription
- [ ] WebSocket support
- [ ] Docker deployment
- [ ] Kubernetes deployment
- [ ] Multi-file batch UI
- [ ] Custom vocabulary
- [ ] Speaker identification/labeling
- [ ] Emotion detection
- [ ] More output formats (VTT, DOCX, PDF)
- [ ] Cloud deployment guides
- [ ] Translation to multiple languages
- [ ] Mobile app (React Native)

### Completed

- [x] CLI interface
- [x] Web interface
- [x] REST API
- [x] Speaker diarization
- [x] Multi-language support
- [x] Translation to English
- [x] Multiple output formats
- [x] GPU/CPU support

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

### Third-Party Licenses

- **Whisper**: MIT License © OpenAI
- **Pyannote**: MIT License
- **Helsinki-NLP OPUS-MT**: Apache 2.0
- **FastAPI**: MIT License
- **Next.js**: MIT License
- **PyTorch**: BSD-3-Clause

---

## 🙏 Acknowledgments

Built with amazing open-source projects:

- **[OpenAI Whisper](https://github.com/openai/whisper)** - State-of-the-art speech recognition
- **[Pyannote Audio](https://github.com/pyannote/pyannote-audio)** - Speaker diarization
- **[Helsinki-NLP](https://huggingface.co/Helsinki-NLP)** - Translation models
- **[FastAPI](https://fastapi.tiangolo.com/)** - Modern Python web framework
- **[Next.js](https://nextjs.org/)** - React framework for production
- **[HuggingFace](https://huggingface.co/)** - Model hosting and transformers library
- **[FFmpeg](https://ffmpeg.org/)** - Audio processing

---

## 📞 Support

### Get Help

- **Documentation:** [README.md](README.md), [SETUP.md](SETUP.md), [USAGE.md](USAGE.md)
- **Issues:** [GitHub Issues](https://github.com/yourusername/multilingual-transcriber/issues)
- **Discussions:** [GitHub Discussions](https://github.com/yourusername/multilingual-transcriber/discussions)

### Community

- Star the repo if you find it useful! ⭐
- Share with others who might benefit
- Contribute improvements and bug fixes

---

## 📈 Stats

![GitHub stars](https://img.shields.io/github/stars/yourusername/multilingual-transcriber?style=social)
![GitHub forks](https://img.shields.io/github/forks/yourusername/multilingual-transcriber?style=social)
![GitHub issues](https://img.shields.io/github/issues/yourusername/multilingual-transcriber)
![GitHub license](https://img.shields.io/github/license/yourusername/multilingual-transcriber)

---

<div align="center">

## 🧠 Production Upgrade

This codebase now includes a retrieval-augmented backend that can ingest documents or transcripts, chunk them for semantic search, and return grounded answers with citations.

### What Changed
- Added a persistent vector store with FAISS support when available and a TF-IDF fallback for local development.
- Added structured prompt builders, answer validation, and hallucination-risk checks.
- Added an evaluation harness with relevance, correctness, consistency, and groundedness metrics.
- Added FastAPI routes for RAG ingestion, querying, and evaluation.
- **NEW**: Added Ollama integration for LLM-based answer generation with automatic fallback to context-only if Ollama is unavailable.

### New Backend Layout
```text
backend/
├── rag/
│   ├── chunking.py
│   ├── embeddings.py
│   ├── evaluation.py
│   ├── generator.py          ← NEW: Ollama + fallback generators
│   ├── prompts.py
│   ├── service.py
│   ├── validation.py
│   └── vector_store.py
└── storage/
    └── vector_store/
```

### LLM Generation with Ollama

The RAG system now supports local LLM inference via [Ollama](https://ollama.ai) for grounded answer generation:

#### Setup Ollama (Optional but Recommended)

1. **Install Ollama**:
   - macOS: `brew install ollama`
   - Linux: `curl -fsSL https://ollama.ai/install.sh | sh`
   - Windows: Download from https://ollama.ai

2. **Pull a Model**:
   ```bash
   ollama pull mistral      # Recommended: 7B, fast, good quality
   # OR
   ollama pull neural-chat  # 7B, conversational optimized
   # OR
   ollama pull orca-mini    # 3B, lightweight
   ```

3. **Start Ollama Server**:
   ```bash
   ollama serve
   # Runs on http://localhost:11434 by default
   ```

#### Query the RAG System with LLM

**With LLM generation (default)**:
```bash
curl -X POST http://localhost:8000/rag/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is this document about?",
    "top_k": 5,
    "use_llm": true
  }'
```

**Without LLM (context-only fallback)**:
```bash
curl -X POST http://localhost:8000/rag/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is this document about?",
    "top_k": 5,
    "use_llm": false
  }'
```

#### Response Structure
```json
{
  "question": "What is this document about?",
  "answer": "The LLM-generated grounded answer with citations [source:chunk_id]...",
  "prompt": "Full prompt sent to the LLM",
  "messages": [
    {"role": "system", "content": "Answer only from provided context..."},
    {"role": "developer", "content": "Use concise style..."},
    {"role": "user", "content": "...full context and question..."}
  ],
  "retrieval": [
    {
      "chunk_id": "doc1:chunk_0",
      "document_id": "doc1",
      "source": "example.txt",
      "score": 0.89,
      "text": "Relevant text from document..."
    }
  ],
  "validation": {
    "is_grounded": true,
    "groundedness_score": 0.95,
    "citations": ["chunk_0", "chunk_2"],
    "unsupported_ratio": 0.05,
    "warnings": []
  }
}
```

#### Automatic Fallback

If Ollama is not available:
- The system automatically detects this during startup
- Falls back to `SimpleContextGenerator` (returns formatted context)
- All queries still work, but `answer` field contains context summary instead of LLM output
- No configuration needed—fully automatic

#### RAG Ingestion Pipeline

Auto-index transcripts for Q&A:
```bash
# After transcription, transcript is automatically indexed
curl -X POST http://localhost:8000/rag/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "source_name": "Meeting Notes",
    "text": "Meeting discussion...",
    "document_id": "meeting-2025-01-01",
    "metadata": {"date": "2025-01-01", "type": "meeting"}
  }'
```

#### Evaluation & Quality Metrics

Run the evaluation suite:
```bash
curl -X POST http://localhost:8000/rag/evaluate
```

Returns metrics:
- **Token F1**: Overlap between generated answer and ground truth
- **Jaccard Similarity**: Set-based overlap
- **Relevance**: Is context relevant to question?
- **Correctness**: Is answer factually accurate?
- **Consistency**: Are multiple answers consistent?
- **Groundedness**: Does answer stay within context?

---

**Made with ❤️ for the open-source community**

If this project helped you, consider giving it a ⭐️ on GitHub!

[⬆ Back to Top](#-multilingual-audio-transcriber--translator)

</div>
