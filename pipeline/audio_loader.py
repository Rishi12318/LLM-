"""Audio loading and preprocessing module."""

import torch
import torchaudio
from pathlib import Path
from typing import Tuple
from pydub import AudioSegment
from rich.console import Console
import tempfile
import os

console = Console()


def load_audio(file_path: str, target_sr: int = 16000) -> Tuple[torch.Tensor, int]:
    """
    Load audio file and convert to mono 16kHz torch tensor.
    
    Supports multiple formats: WAV, MP3, M4A, FLAC, OGG, etc.
    
    Args:
        file_path: Path to audio file
        target_sr: Target sample rate (default: 16000 Hz for Whisper)
        
    Returns:
        Tuple of (audio_tensor, sample_rate)
        - audio_tensor: 1D tensor of audio samples
        - sample_rate: Sample rate in Hz
        
    Raises:
        FileNotFoundError: If audio file doesn't exist
        Exception: If audio loading fails
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"Audio file not found: {file_path}")
    
    console.print(f"📂 Loading audio: {file_path.name}")
    
    try:
        # Try loading directly with torchaudio first (fastest for WAV files)
        try:
            waveform, sample_rate = torchaudio.load(str(file_path))
            console.print(f"   Format: {file_path.suffix.upper()}, {sample_rate} Hz")
            
        except Exception:
            # Fallback to pydub for other formats (MP3, M4A, etc.)
            console.print(f"   Using pydub for format conversion...")
            audio = AudioSegment.from_file(str(file_path))
            
            # Convert to mono
            if audio.channels > 1:
                audio = audio.set_channels(1)
            
            # Export to temporary WAV for loading
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                tmp_path = tmp_file.name
                audio.export(tmp_path, format="wav")
                waveform, sample_rate = torchaudio.load(tmp_path)
                os.unlink(tmp_path)
            
            console.print(f"   Converted from {file_path.suffix.upper()}, {audio.frame_rate} Hz")
        
        # Convert to mono if stereo
        if waveform.shape[0] > 1:
            waveform = torch.mean(waveform, dim=0, keepdim=True)
            console.print("   Converted to mono")
        
        # Resample to target sample rate if needed
        if sample_rate != target_sr:
            resampler = torchaudio.transforms.Resample(
                orig_freq=sample_rate,
                new_freq=target_sr
            )
            waveform = resampler(waveform)
            console.print(f"   Resampled to {target_sr} Hz")
            sample_rate = target_sr
        
        # Squeeze to 1D tensor
        waveform = waveform.squeeze(0)
        
        # Calculate duration
        duration = len(waveform) / sample_rate
        console.print(f"✓ Audio loaded: {duration:.2f} seconds", style="green")
        
        return waveform, sample_rate
        
    except Exception as e:
        console.print(f"❌ Failed to load audio: {e}", style="red")
        raise


def audio_to_numpy(audio_tensor: torch.Tensor) -> "numpy.ndarray":
    """
    Convert torch tensor to numpy array for compatibility.
    
    Args:
        audio_tensor: PyTorch audio tensor
        
    Returns:
        Numpy array of audio samples
    """
    import numpy as np
    return audio_tensor.cpu().numpy()


def validate_audio_format(file_path: str) -> bool:
    """
    Validate if the file is a supported audio format.
    
    Args:
        file_path: Path to audio file
        
    Returns:
        True if format is supported, False otherwise
    """
    supported_formats = {".wav", ".mp3", ".m4a", ".flac", ".ogg", ".opus", ".webm"}
    file_ext = Path(file_path).suffix.lower()
    return file_ext in supported_formats


def get_audio_info(file_path: str) -> dict:
    """
    Get audio file metadata without loading the entire file.
    
    Args:
        file_path: Path to audio file
        
    Returns:
        Dictionary with audio metadata
    """
    try:
        audio = AudioSegment.from_file(file_path)
        return {
            "duration": len(audio) / 1000.0,  # Convert ms to seconds
            "channels": audio.channels,
            "sample_rate": audio.frame_rate,
            "sample_width": audio.sample_width,
            "format": Path(file_path).suffix[1:].upper(),
        }
    except Exception as e:
        return {"error": str(e)}
