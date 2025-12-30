"""Whisper-based automatic speech recognition with language detection."""

import torch
import whisper
from typing import Tuple, List, Dict
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


def whisper_transcribe(
    audio: torch.Tensor,
    sample_rate: int,
    model_name: str = "large-v3",
    device: str = "auto"
) -> Tuple[str, List[Dict]]:
    """
    Transcribe audio using OpenAI Whisper with automatic language detection.
    
    Args:
        audio: Audio tensor (1D, mono)
        sample_rate: Sample rate in Hz (should be 16000 for Whisper)
        model_name: Whisper model size (tiny, base, small, medium, large, large-v3)
        device: Device to use ("cuda", "cpu", or "auto")
        
    Returns:
        Tuple of (language_code, segments)
        - language_code: Detected ISO 639-1 language code
        - segments: List of transcription segments with timestamps
          [{"start": 0.0, "end": 2.5, "text": "Hello world"}]
    """
    console.print("\n🗣️  SPEECH RECOGNITION", style="bold yellow")
    console.print("─" * 60)
    
    # Auto-detect device
    if device == "auto":
        if torch.cuda.is_available():
            device = "cuda"
        elif torch.backends.mps.is_available():
            device = "mps"
        else:
            device = "cpu"
    
    console.print(f"Loading Whisper model: {model_name} on {device}")
    
    try:
        # Load Whisper model (auto-downloads on first use)
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Loading model...", total=None)
            model = whisper.load_model(model_name, device=device)
            progress.update(task, completed=True)
        
        console.print("✓ Model loaded", style="green")
        
        # Convert tensor to numpy for Whisper
        audio_np = audio.cpu().numpy()
        
        # Detect language first
        console.print("\nDetecting language...")
        audio_segment = whisper.pad_or_trim(audio_np)
        mel = whisper.log_mel_spectrogram(audio_segment, n_mels=model.dims.n_mels).to(model.device)
        _, probs = model.detect_language(mel)
        detected_lang = max(probs, key=probs.get)
        confidence = probs[detected_lang]
        
        console.print(f"✓ Detected: {detected_lang.upper()} (confidence: {confidence:.2%})", style="green")
        
        # Transcribe with timestamps
        console.print("\nTranscribing...")
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Processing audio...", total=None)
            
            result = model.transcribe(
                audio_np,
                language=detected_lang,
                task="transcribe",
                verbose=False,
                word_timestamps=False,
            )
            
            progress.update(task, completed=True)
        
        # Extract segments with timestamps
        segments = []
        for segment in result["segments"]:
            segments.append({
                "start": segment["start"],
                "end": segment["end"],
                "text": segment["text"].strip(),
            })
        
        console.print(f"✓ Transcribed {len(segments)} segments", style="green")
        
        # Show sample
        if segments:
            sample_text = segments[0]["text"][:100]
            console.print(f'\nSample: "{sample_text}..."', style="dim")
        
        return detected_lang, segments
        
    except Exception as e:
        console.print(f"❌ Transcription failed: {e}", style="red")
        raise


def format_transcription(segments: List[Dict], lang_code: str) -> str:
    """
    Format transcription segments into readable text.
    
    Args:
        segments: List of transcription segments
        lang_code: Language code
        
    Returns:
        Formatted transcription string
    """
    lines = [f"Language: {lang_code.upper()}\n"]
    
    for seg in segments:
        timestamp = f"[{seg['start']:.2f}s - {seg['end']:.2f}s]"
        lines.append(f"{timestamp} {seg['text']}")
    
    return "\n".join(lines)


def get_full_transcript(segments: List[Dict]) -> str:
    """
    Get full transcript text without timestamps.
    
    Args:
        segments: List of transcription segments
        
    Returns:
        Complete transcript as single string
    """
    return " ".join(seg["text"] for seg in segments)


def filter_segments_by_duration(
    segments: List[Dict],
    min_duration: float = 0.5,
    max_duration: float = 30.0
) -> List[Dict]:
    """
    Filter segments by duration constraints.
    
    Args:
        segments: List of transcription segments
        min_duration: Minimum segment duration in seconds
        max_duration: Maximum segment duration in seconds
        
    Returns:
        Filtered list of segments
    """
    filtered = []
    for seg in segments:
        duration = seg["end"] - seg["start"]
        if min_duration <= duration <= max_duration:
            filtered.append(seg)
    
    return filtered
