"""
Installation and Usage Examples
================================

This script demonstrates how to install and use the multilingual transcriber.
"""

# ============================================================================
# STEP 1: INSTALLATION
# ============================================================================

"""
# Install all dependencies:
pip install -r requirements.txt

# This will install:
# - PyTorch (deep learning)
# - Whisper (speech recognition)
# - Pyannote (speaker diarization)
# - Transformers (translation)
# - Rich & Typer (CLI)
# - Audio processing libraries

# First installation may take 5-10 minutes
"""

# ============================================================================
# STEP 2: BASIC USAGE (CLI)
# ============================================================================

"""
# Test with included sample
python main.py sample.wav

# Process your own audio file
python main.py your_audio.mp3

# With specific options
python main.py audio.wav --model large-v3 --device cuda

# Skip diarization (faster)
python main.py audio.wav --skip-diarization

# Custom output directory
python main.py audio.wav --output-dir ./my_results
"""

# ============================================================================
# STEP 3: PYTHON API USAGE
# ============================================================================

"""
# Example: Using as Python module

from pipeline import (
    load_audio,
    whisper_transcribe, 
    pyannote_diarize,
    align_segments,
    batch_translate
)
from pipeline.format_output import save_all_formats

# Load audio file
audio, sample_rate = load_audio("audio.wav")

# Transcribe with language detection
lang_code, segments = whisper_transcribe(audio, sample_rate)

# Identify speakers
speaker_segments = pyannote_diarize(audio, sample_rate)

# Align text with speakers
aligned = align_segments(segments, speaker_segments, lang_code)

# Translate to English
translated = batch_translate(aligned, lang_code)

# Save all formats
save_all_formats(translated, "./output", "result")
"""

# ============================================================================
# STEP 4: ADVANCED EXAMPLES
# ============================================================================

"""
# Example 1: Batch processing multiple files
import os
from pathlib import Path

audio_files = Path("./audio_folder").glob("*.mp3")
for audio_file in audio_files:
    os.system(f"python main.py {audio_file} --output-dir ./results/{audio_file.stem}")

# Example 2: Using smaller model for speed
python main.py audio.wav --model medium --device cuda

# Example 3: Processing long audio on CPU
python main.py long_audio.wav --model base --device cpu --skip-diarization

# Example 4: Specify number of speakers
python main.py audio.wav --min-speakers 2 --max-speakers 3
"""

# ============================================================================
# STEP 5: COMMON WORKFLOWS
# ============================================================================

"""
# Workflow 1: Quick transcription (no speakers)
python main.py audio.wav --skip-diarization --model medium

# Workflow 2: High accuracy with speakers
python main.py audio.wav --model large-v3 --device cuda

# Workflow 3: Batch translate multiple languages
for file in *.mp3; do
    python main.py "$file" --output-dir results/
done

# Workflow 4: Generate only SRT subtitles
# (Process normally, then use the generated SRT files from output/)
"""

# ============================================================================
# STEP 6: TROUBLESHOOTING
# ============================================================================

"""
# Check system compatibility
python main.py test

# View model information
python main.py info

# If CUDA out of memory
python main.py audio.wav --model medium --device cuda
# or
python main.py audio.wav --device cpu

# If pyannote authentication fails
python main.py audio.wav --skip-diarization

# Install HuggingFace CLI and login
pip install huggingface_hub
huggingface-cli login
"""

# ============================================================================
# STEP 7: CUSTOMIZATION
# ============================================================================

"""
# Modify models/config.py to:
# - Add new translation language pairs
# - Change default Whisper model
# - Adjust model configurations

# Modify pipeline modules to:
# - Add custom preprocessing
# - Implement additional output formats
# - Tune alignment parameters

# Example: Add custom output format
from pipeline.format_output import save_json

def save_custom_format(segments, output_path):
    # Your custom formatting logic
    pass
"""

# ============================================================================
# STEP 8: PERFORMANCE OPTIMIZATION
# ============================================================================

"""
# For faster processing:

1. Use GPU (10-20x faster)
   python main.py audio.wav --device cuda

2. Use smaller model for testing
   python main.py audio.wav --model medium

3. Skip diarization if not needed
   python main.py audio.wav --skip-diarization

4. Batch process with multiprocessing
   # Process multiple files in parallel (CPU cores)
   from multiprocessing import Pool
   
   def process_file(file):
       os.system(f"python main.py {file}")
   
   with Pool(4) as p:
       p.map(process_file, audio_files)
"""

# ============================================================================
# READY TO USE!
# ============================================================================

print("""
╔═══════════════════════════════════════════════════════════╗
║            MULTILINGUAL TRANSCRIBER - READY!              ║
╚═══════════════════════════════════════════════════════════╝

📦 Installation:
   pip install -r requirements.txt

🚀 Quick Start:
   python main.py sample.wav

📖 Documentation:
   - README.md: Complete guide
   - SETUP.md: Installation help
   - PROJECT_SUMMARY.md: Overview

💡 Examples:
   python main.py audio.wav
   python main.py audio.mp3 --model large-v3 --device cuda
   python main.py audio.wav --skip-diarization

🔧 Utilities:
   python main.py test  # System check
   python main.py info  # Model information
   python main.py --help  # All options

✨ Features:
   ✓ 100+ languages auto-detection
   ✓ Speaker diarization
   ✓ English translation
   ✓ Multiple output formats
   ✓ 100% offline after setup
   ✓ GPU/CPU support

Happy transcribing! 🎙️
""")
