"""Pyannote-based speaker diarization module."""

import torch
from typing import List, Dict
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
import warnings

# Suppress pyannote warnings
warnings.filterwarnings("ignore", category=UserWarning)

console = Console()


def pyannote_diarize(
    audio: torch.Tensor,
    sample_rate: int,
    model_name: str = "pyannote/speaker-diarization-3.1",
    device: str = "auto",
    min_speakers: int = 1,
    max_speakers: int = None
) -> List[Dict]:
    """
    Perform speaker diarization using Pyannote.
    
    Args:
        audio: Audio tensor (1D, mono)
        sample_rate: Sample rate in Hz
        model_name: Pyannote model identifier
        device: Device to use ("cuda", "cpu", or "auto")
        min_speakers: Minimum number of speakers (default: 1)
        max_speakers: Maximum number of speakers (default: None = auto-detect)
        
    Returns:
        List of speaker segments
        [{"start": 0.0, "end": 2.5, "speaker": "SPEAKER_00"}]
    """
    console.print("\n👥 SPEAKER DIARIZATION", style="bold yellow")
    console.print("─" * 60)
    
    # Auto-detect device
    if device == "auto":
        if torch.cuda.is_available():
            device = "cuda"
        elif torch.backends.mps.is_available():
            device = "mps"
        else:
            device = "cpu"
    
    try:
        from pyannote.audio import Pipeline
        import torchaudio
        
        console.print(f"Loading diarization model: {model_name}")
        
        # Load pipeline (requires HuggingFace token for first-time download)
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Loading pipeline...", total=None)
            
            try:
                pipeline = Pipeline.from_pretrained(
                    model_name,
                    use_auth_token=None  # Will prompt if needed
                )
                pipeline = pipeline.to(torch.device(device))
            except Exception as e:
                if "token" in str(e).lower() or "authentication" in str(e).lower():
                    console.print("\n⚠️  Pyannote requires HuggingFace authentication", style="yellow")
                    console.print("   Please accept the model conditions at:", style="yellow")
                    console.print(f"   https://huggingface.co/{model_name}", style="cyan")
                    console.print("\n   Then run: huggingface-cli login", style="yellow")
                raise
            
            progress.update(task, completed=True)
        
        console.print("✓ Pipeline loaded", style="green")
        
        # Prepare audio for Pyannote (needs to be 2D: [channels, samples])
        if audio.dim() == 1:
            audio = audio.unsqueeze(0)
        
        # Create a temporary in-memory audio file
        console.print("\nProcessing audio...")
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Identifying speakers...", total=None)
            
            # Pyannote expects dictionary with waveform and sample_rate
            audio_dict = {
                "waveform": audio,
                "sample_rate": sample_rate
            }
            
            # Run diarization
            diarization = pipeline(
                audio_dict,
                min_speakers=min_speakers,
                max_speakers=max_speakers
            )
            
            progress.update(task, completed=True)
        
        # Extract segments
        segments = []
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            segments.append({
                "start": turn.start,
                "end": turn.end,
                "speaker": speaker
            })
        
        # Count unique speakers
        unique_speakers = len(set(seg["speaker"] for seg in segments))
        console.print(f"✓ Found {unique_speakers} speaker(s) in {len(segments)} segments", style="green")
        
        return segments
        
    except ImportError:
        console.print("❌ Pyannote not installed. Install with: pip install pyannote.audio", style="red")
        raise
    except Exception as e:
        console.print(f"❌ Diarization failed: {e}", style="red")
        # Return empty segments as fallback
        console.print("⚠️  Continuing without speaker separation", style="yellow")
        return []


def merge_continuous_segments(segments: List[Dict], gap_threshold: float = 0.5) -> List[Dict]:
    """
    Merge continuous segments from the same speaker.
    
    Args:
        segments: List of speaker segments
        gap_threshold: Maximum gap (seconds) to merge
        
    Returns:
        Merged list of segments
    """
    if not segments:
        return []
    
    merged = []
    current = segments[0].copy()
    
    for seg in segments[1:]:
        # If same speaker and gap is small, merge
        if (seg["speaker"] == current["speaker"] and 
            seg["start"] - current["end"] <= gap_threshold):
            current["end"] = seg["end"]
        else:
            merged.append(current)
            current = seg.copy()
    
    merged.append(current)
    return merged


def rename_speakers(segments: List[Dict]) -> List[Dict]:
    """
    Rename speakers from SPEAKER_XX to Speaker 1, Speaker 2, etc.
    
    Args:
        segments: List of speaker segments
        
    Returns:
        Segments with renamed speakers
    """
    if not segments:
        return []
    
    # Get unique speakers in order of first appearance
    speaker_map = {}
    speaker_count = 1
    
    for seg in segments:
        if seg["speaker"] not in speaker_map:
            speaker_map[seg["speaker"]] = f"Speaker {speaker_count}"
            speaker_count += 1
    
    # Rename all segments
    renamed = []
    for seg in segments:
        seg_copy = seg.copy()
        seg_copy["speaker"] = speaker_map[seg["speaker"]]
        renamed.append(seg_copy)
    
    return renamed


def get_speaker_statistics(segments: List[Dict]) -> Dict:
    """
    Get statistics about speakers.
    
    Args:
        segments: List of speaker segments
        
    Returns:
        Dictionary with speaker statistics
    """
    if not segments:
        return {"total_speakers": 0, "speaker_times": {}}
    
    speaker_times = {}
    for seg in segments:
        speaker = seg["speaker"]
        duration = seg["end"] - seg["start"]
        speaker_times[speaker] = speaker_times.get(speaker, 0) + duration
    
    return {
        "total_speakers": len(speaker_times),
        "speaker_times": speaker_times,
        "total_duration": sum(speaker_times.values())
    }
