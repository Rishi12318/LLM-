# 🎙️ Multilingual Audio Transcriber & Translator

A **100% offline**, fully self-contained CLI tool for automatic speech recognition with speaker diarization and translation to English. All models are automatically downloaded and cached on first run—no API keys required!

## ✨ Features

- 🌍 **100+ Languages** - Auto-detection with Whisper Large V3
- 👥 **Speaker Diarization** - Identifies who spoke when using Pyannote 3.1
- 🔄 **Auto-Translation** - Translates to English using Helsinki-NLP models
- 📄 **Multiple Formats** - Outputs JSON, Markdown, SRT subtitles, and plain text
- 🚀 **100% Offline** - All models bundled, works after initial download
- 🖥️ **GPU/CPU Support** - Auto-detects CUDA, MPS, or CPU
- 🎵 **Universal Audio** - Supports WAV, MP3, M4A, FLAC, OGG, etc.

## 🚀 Quick Start

### Installation

```bash
# Clone or download this repository
cd multilingual-transcriber

# Install dependencies
pip install -r requirements.txt

# Optional: Install FFmpeg for audio format support
# Windows (with Chocolatey): choco install ffmpeg
# macOS: brew install ffmpeg
# Linux: sudo apt-get install ffmpeg
```

### Basic Usage

```bash
# Transcribe any audio file
python main.py audio.wav

# Use a specific Whisper model
python main.py audio.mp3 --model large-v3

# Force CPU or GPU
python main.py audio.wav --device cuda
python main.py audio.wav --device cpu

# Skip speaker diarization (faster)
python main.py audio.wav --skip-diarization

# Custom output directory
python main.py audio.wav --output-dir ./my_results
```

### System Check

```bash
# Check if all dependencies are installed
python main.py test

# View model information
python main.py info
```

## 📦 What Gets Downloaded (First Run)

On first run, the following models are automatically downloaded (~5-7GB total):

1. **Whisper Large V3** (~3GB) - Multilingual speech recognition
2. **Pyannote Speaker Diarization 3.1** (~1GB) - Speaker separation
3. **Helsinki-NLP Translation Models** (~500MB per language) - Translation to English

Models are cached in `~/.cache/huggingface/` and reused for subsequent runs.

## 📋 Complete Example

```bash
# Process a Hindi audio file
python main.py hindi_conversation.wav
```

**Output:**

```
╔═══════════════════════════════════════════════════════════╗
║  🎙️  MULTILINGUAL AUDIO TRANSCRIBER & TRANSLATOR  🌐    ║
║                                                           ║
║  100+ Languages • Speaker Diarization • Auto-Translation ║
╚═══════════════════════════════════════════════════════════╝

🔄 STEP 1: LOADING AUDIO
📂 Loading audio: hindi_conversation.wav
✓ Audio loaded: 45.2 seconds

🔄 STEP 2: SPEECH RECOGNITION
Loading Whisper model: large-v3 on cuda
✓ Detected: HI (confidence: 99.8%)
✓ Transcribed 12 segments

🔄 STEP 3: SPEAKER DIARIZATION
✓ Found 2 speaker(s) in 18 segments

🔄 STEP 4: ALIGNING SPEAKERS & TEXT
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

| Model | Size | Speed | Accuracy |
|-------|------|-------|----------|
| `tiny` | ~75MB | Fastest | Low |
| `base` | ~150MB | Very Fast | Medium |
| `small` | ~500MB | Fast | Good |
| `medium` | ~1.5GB | Moderate | Very Good |
| `large` | ~3GB | Slow | Excellent |
| `large-v3` | ~3GB | Slow | Best |

## 🌍 Supported Languages

The system auto-detects and supports **100+ languages**, including:

| Language | Code | Translation |
|----------|------|-------------|
| English | en | ✓ (native) |
| Hindi | hi | ✓ |
| Spanish | es | ✓ |
| French | fr | ✓ |
| German | de | ✓ |
| Italian | it | ✓ |
| Portuguese | pt | ✓ |
| Russian | ru | ✓ |
| Japanese | ja | ✓ |
| Korean | ko | ✓ |
| Chinese | zh | ✓ |
| Arabic | ar | ✓ |
| Tamil | ta | ✓ |
| Telugu | te | ✓ |
| Turkish | tr | ✓ |
| And 85+ more... | | ✓ |

## 🔧 Advanced Usage

### Python API

```python
from pipeline import load_audio, whisper_transcribe, pyannote_diarize, align_segments, batch_translate
from pipeline.format_output import save_all_formats

# Load audio
audio, sr = load_audio("audio.wav")

# Transcribe
lang, segments = whisper_transcribe(audio, sr, model_name="large-v3")

# Diarize
speakers = pyannote_diarize(audio, sr)

# Align
aligned = align_segments(segments, speakers, lang)

# Translate
translated = batch_translate(aligned, lang)

# Save
save_all_formats(translated, "./output", "result")
```

## 📊 Performance

| Audio Duration | Whisper Model | Device | Processing Time |
|----------------|---------------|--------|-----------------|
| 1 min | large-v3 | RTX 3090 | ~15 sec |
| 1 min | large-v3 | CPU (i9) | ~2 min |
| 10 min | large-v3 | RTX 3090 | ~2 min |
| 10 min | medium | RTX 3090 | ~1 min |

## 🛠️ Troubleshooting

### FFmpeg Not Found

**Windows:**
```bash
choco install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt-get install ffmpeg
```

### Pyannote Authentication Error

Pyannote models require accepting terms on HuggingFace:

1. Visit https://huggingface.co/pyannote/speaker-diarization-3.1
2. Accept the model conditions
3. Run: `huggingface-cli login`
4. Paste your HuggingFace token

### CUDA Out of Memory

Use a smaller model:
```bash
python main.py audio.wav --model medium
```

Or force CPU:
```bash
python main.py audio.wav --device cpu
```

## 📁 Project Structure

```
multilingual-transcriber/
├── main.py                 # CLI entrypoint
├── pipeline/
│   ├── audio_loader.py     # Audio loading and preprocessing
│   ├── whisper_asr.py      # Speech recognition
│   ├── pyannote_diar.py    # Speaker diarization
│   ├── align_segments.py   # Speaker-text alignment
│   ├── translate.py        # Translation
│   └── format_output.py    # Output formatting
├── models/
│   ├── config.py           # Model configurations
│   └── cache_manager.py    # Auto-download management
├── utils/
│   └── helpers.py          # Utility functions
├── requirements.txt        # Dependencies
├── pyproject.toml          # Poetry config (optional)
└── README.md              # This file
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

MIT License - feel free to use this project for personal or commercial purposes.

## 🙏 Acknowledgments

- [OpenAI Whisper](https://github.com/openai/whisper) - Speech recognition
- [Pyannote Audio](https://github.com/pyannote/pyannote-audio) - Speaker diarization
- [Helsinki-NLP](https://huggingface.co/Helsinki-NLP) - Translation models
- [HuggingFace](https://huggingface.co/) - Model hosting

## 📮 Support

For issues, questions, or suggestions, please open an issue on GitHub.

---

Made with ❤️ using AI/ML models | 100% Offline | No API Keys Required
