# Quick Setup Guide

## Prerequisites

- Python 3.9 or higher
- pip package manager
- FFmpeg (for audio format support)

## Installation Steps

### 1. Install FFmpeg

**Windows (using Chocolatey):**
```bash
choco install ffmpeg
```

**Windows (manual):**
1. Download from https://ffmpeg.org/download.html
2. Extract to C:\ffmpeg
3. Add C:\ffmpeg\bin to System PATH

**macOS:**
```bash
brew install ffmpeg
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

### 2. Install Python Dependencies

```bash
# Navigate to project directory
cd multilingual-transcriber

# Install all dependencies
pip install -r requirements.txt
```

**Note:** First installation may take 5-10 minutes due to large packages (PyTorch, Transformers).

### 3. (Optional) Setup HuggingFace Authentication

For speaker diarization, you need to accept Pyannote model terms:

1. Create a free HuggingFace account at https://huggingface.co
2. Visit https://huggingface.co/pyannote/speaker-diarization-3.1
3. Accept the model conditions
4. Create an access token at https://huggingface.co/settings/tokens
5. Login via CLI:
   ```bash
   huggingface-cli login
   ```

**Or skip diarization:**
```bash
python main.py audio.wav --skip-diarization
```

### 4. Verify Installation

```bash
# Run system check
python main.py test

# Should show all components with ✓
```

### 5. First Run

```bash
# Test with sample audio
python main.py sample.wav

# Or with your own file
python main.py your_audio.mp3
```

**First run notes:**
- Whisper models (~3GB) will auto-download
- Translation models (~500MB per language) download on-demand
- Models are cached for future use
- Total download: 3-7GB depending on languages used

## Troubleshooting

### "FFmpeg not found"
- Ensure FFmpeg is installed and in PATH
- Restart terminal after installation
- Test: `ffmpeg -version`

### "CUDA out of memory"
```bash
# Use smaller model
python main.py audio.wav --model medium

# Or force CPU
python main.py audio.wav --device cpu
```

### "Pyannote authentication failed"
```bash
# Skip diarization
python main.py audio.wav --skip-diarization

# Or complete HuggingFace authentication (see step 3)
```

### Import errors
```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

## Quick Start Commands

```bash
# Basic transcription
python main.py audio.wav

# With GPU
python main.py audio.wav --device cuda

# Smaller/faster model
python main.py audio.wav --model medium

# Skip speaker separation (faster)
python main.py audio.wav --skip-diarization

# Custom output location
python main.py audio.wav --output-dir ./my_results

# Show help
python main.py --help
```

## Performance Tips

1. **Use GPU** if available (10-20x faster)
2. **Start with medium model** for testing (faster, still accurate)
3. **Skip diarization** if you don't need speaker separation
4. **Upgrade to large-v3** for best accuracy on final runs

## System Requirements

### Minimum (CPU)
- 8GB RAM
- 10GB free disk space
- Processing: ~2min per 1min audio (large-v3)

### Recommended (GPU)
- 16GB RAM
- NVIDIA GPU with 6GB+ VRAM
- 10GB free disk space
- Processing: ~15sec per 1min audio (large-v3)

## Next Steps

1. ✅ Complete installation
2. ✅ Run `python main.py test` to verify
3. ✅ Try with `sample.wav`: `python main.py sample.wav`
4. ✅ Process your own audio files
5. 📖 Read README.md for advanced usage

## Support

- Check README.md for detailed documentation
- Run `python main.py --help` for all options
- Run `python main.py info` for system information

Enjoy transcribing! 🎙️
