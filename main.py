"""
Multilingual Audio Transcription & Translation System
======================================================

A fully self-contained CLI tool for automatic speech recognition with speaker
diarization and translation to English.

Features:
- 100+ languages auto-detection
- Speaker separation (who spoke when)
- Original + English translation
- Multiple output formats (JSON, Markdown, SRT, Text)
- 100% offline after initial model download
- GPU/CPU auto-detection

Usage:
    python main.py audio.wav
    python main.py audio.mp3 --model large-v3 --device cuda
"""

import sys
from pathlib import Path
from typing import Optional
import time

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from pipeline import (
    load_audio,
    whisper_transcribe,
    pyannote_diarize,
    align_segments,
    batch_translate,
)
from pipeline.format_output import save_all_formats
from models import ModelManager
from utils.helpers import create_output_directory, seconds_to_readable

app = typer.Typer(help="Multilingual Audio Transcription & Translation")
console = Console()


def print_banner():
    """Print application banner."""
    banner = """
    ╔═══════════════════════════════════════════════════════════╗
    ║  🎙️  MULTILINGUAL AUDIO TRANSCRIBER & TRANSLATOR  🌐    ║
    ║                                                           ║
    ║  100+ Languages • Speaker Diarization • Auto-Translation ║
    ╚═══════════════════════════════════════════════════════════╝
    """
    console.print(banner, style="bold cyan")


@app.command()
def transcribe(
    audio_file: str = typer.Argument(..., help="Path to audio file (WAV, MP3, M4A, etc.)"),
    output_dir: Optional[str] = typer.Option(
        "./output",
        "--output-dir", "-o",
        help="Output directory for results"
    ),
    model: str = typer.Option(
        "large-v3",
        "--model", "-m",
        help="Whisper model size (tiny, base, small, medium, large, large-v3)"
    ),
    device: str = typer.Option(
        "auto",
        "--device", "-d",
        help="Device to use (cuda, cpu, mps, or auto)"
    ),
    skip_diarization: bool = typer.Option(
        False,
        "--skip-diarization",
        help="Skip speaker diarization (faster but no speaker labels)"
    ),
    min_speakers: int = typer.Option(
        1,
        "--min-speakers",
        help="Minimum number of speakers for diarization"
    ),
    max_speakers: Optional[int] = typer.Option(
        None,
        "--max-speakers",
        help="Maximum number of speakers for diarization"
    ),
):
    """
    Transcribe and translate audio file with speaker diarization.
    
    Example:
        python main.py audio.wav
        python main.py audio.mp3 --model large-v3 --device cuda
        python main.py audio.wav --skip-diarization
    """
    start_time = time.time()
    
    print_banner()
    
    # Validate audio file
    audio_path = Path(audio_file)
    if not audio_path.exists():
        console.print(f"❌ Audio file not found: {audio_file}", style="bold red")
        raise typer.Exit(1)
    
    # Initialize model manager
    model_manager = ModelManager()
    device = model_manager.get_device() if device == "auto" else device
    
    try:
        # Step 1: Load audio
        console.print("\n" + "="*60, style="bold cyan")
        console.print("🔄 STEP 1: LOADING AUDIO", style="bold cyan")
        console.print("="*60, style="bold cyan")
        
        audio, sample_rate = load_audio(str(audio_path))
        
        # Step 2: Transcribe with Whisper
        console.print("\n" + "="*60, style="bold cyan")
        console.print("🔄 STEP 2: SPEECH RECOGNITION", style="bold cyan")
        console.print("="*60, style="bold cyan")
        
        lang_code, whisper_segments = whisper_transcribe(
            audio, sample_rate, model_name=model, device=device
        )
        
        # Step 3: Speaker diarization (optional)
        if not skip_diarization:
            console.print("\n" + "="*60, style="bold cyan")
            console.print("🔄 STEP 3: SPEAKER DIARIZATION", style="bold cyan")
            console.print("="*60, style="bold cyan")
            
            diar_segments = pyannote_diarize(
                audio, sample_rate, device=device,
                min_speakers=min_speakers, max_speakers=max_speakers
            )
        else:
            console.print("\n⏩ Skipping speaker diarization", style="yellow")
            diar_segments = []
        
        # Step 4: Align segments
        console.print("\n" + "="*60, style="bold cyan")
        console.print("🔄 STEP 4: ALIGNING SPEAKERS & TEXT", style="bold cyan")
        console.print("="*60, style="bold cyan")
        
        aligned_segments = align_segments(whisper_segments, diar_segments, lang_code)
        
        # Step 5: Translate
        console.print("\n" + "="*60, style="bold cyan")
        console.print("🔄 STEP 5: TRANSLATION", style="bold cyan")
        console.print("="*60, style="bold cyan")
        
        translated_segments = batch_translate(aligned_segments, lang_code)
        
        # Step 6: Save outputs
        console.print("\n" + "="*60, style="bold cyan")
        console.print("📄 STEP 6: SAVING OUTPUTS", style="bold cyan")
        console.print("="*60, style="bold cyan")
        
        output_path = create_output_directory(output_dir)
        
        metadata = {
            "source_file": str(audio_path.name),
            "model": model,
            "device": device,
            "diarization_enabled": not skip_diarization,
        }
        
        saved_files = save_all_formats(
            translated_segments,
            str(output_path),
            base_name="result",
            metadata=metadata
        )
        
        # Print summary
        elapsed_time = time.time() - start_time
        print_summary(
            audio_path.name,
            lang_code,
            translated_segments,
            output_path,
            saved_files,
            elapsed_time
        )
        
    except KeyboardInterrupt:
        console.print("\n\n⚠️  Process interrupted by user", style="yellow")
        raise typer.Exit(130)
    except Exception as e:
        console.print(f"\n\n❌ ERROR: {e}", style="bold red")
        raise typer.Exit(1)


def print_summary(
    filename: str,
    lang_code: str,
    segments: list,
    output_path: Path,
    files: dict,
    elapsed_time: float
):
    """Print processing summary."""
    from models.config import get_language_name
    
    console.print("\n" + "="*60, style="bold green")
    console.print("✅ PROCESSING COMPLETE", style="bold green")
    console.print("="*60, style="bold green")
    
    # Create summary table
    table = Table(show_header=True, header_style="bold cyan", show_lines=True)
    table.add_column("Property", style="yellow")
    table.add_column("Value", style="white")
    
    # Calculate stats
    duration = max(seg["end"] for seg in segments) if segments else 0
    num_speakers = len(set(seg["speaker"] for seg in segments))
    num_segments = len(segments)
    
    table.add_row("Audio File", filename)
    table.add_row("Language", f"{get_language_name(lang_code)} ({lang_code})")
    table.add_row("Duration", seconds_to_readable(duration))
    table.add_row("Speakers", str(num_speakers))
    table.add_row("Segments", str(num_segments))
    table.add_row("Processing Time", seconds_to_readable(elapsed_time))
    
    console.print(table)
    
    # Output files
    console.print(f"\n📁 Output Directory: {output_path}", style="bold cyan")
    console.print("\nGenerated Files:", style="bold yellow")
    for format_type, file_path in files.items():
        console.print(f"  ✓ {Path(file_path).name}", style="green")
    
    # Sample output
    if segments:
        console.print("\n📝 Sample Output:", style="bold yellow")
        sample = segments[0]
        console.print(f"  Speaker: {sample['speaker']}", style="cyan")
        console.print(f"  Original: {sample['original'][:100]}...", style="white")
        if sample.get('english') and sample['english'] != sample['original']:
            console.print(f"  English: {sample['english'][:100]}...", style="green")


@app.command()
def info():
    """Display system and model information."""
    print_banner()
    
    model_manager = ModelManager()
    info = model_manager.get_model_info()
    
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Property", style="yellow")
    table.add_column("Value", style="white")
    
    table.add_row("Device", info["device"])
    table.add_row("Cache Directory", info["cache_dir"])
    table.add_row("Available Whisper Models", ", ".join(info["whisper_models"]))
    table.add_row("Diarization Model", info["diarization_model"])
    
    console.print(table)


@app.command()
def test():
    """Run a quick test with system check."""
    print_banner()
    console.print("🔍 Running system checks...\n", style="bold yellow")
    
    # Check imports
    checks = []
    
    try:
        import torch
        checks.append(("PyTorch", "✓", "green"))
    except ImportError:
        checks.append(("PyTorch", "✗", "red"))
    
    try:
        import whisper
        checks.append(("Whisper", "✓", "green"))
    except ImportError:
        checks.append(("Whisper", "✗", "red"))
    
    try:
        import pyannote.audio
        checks.append(("Pyannote", "✓", "green"))
    except ImportError:
        checks.append(("Pyannote", "✗", "red"))
    
    try:
        import transformers
        checks.append(("Transformers", "✓", "green"))
    except ImportError:
        checks.append(("Transformers", "✗", "red"))
    
    try:
        import pydub
        checks.append(("Pydub", "✓", "green"))
    except ImportError:
        checks.append(("Pydub", "✗", "red"))
    
    # Print results
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Component", style="yellow")
    table.add_column("Status", justify="center")
    
    for name, status, color in checks:
        table.add_row(name, f"[{color}]{status}[/{color}]")
    
    console.print(table)
    
    # Check device
    console.print("\n🖥️  Device Info:", style="bold yellow")
    model_manager = ModelManager()
    device = model_manager.get_device()
    console.print(f"   Active device: {device}", style="cyan")


if __name__ == "__main__":
    app()
