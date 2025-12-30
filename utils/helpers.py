"""Helper utilities for timestamp formatting, logging, and duration calculation."""

import logging
from datetime import datetime
from pathlib import Path


def format_timestamp(seconds: float) -> str:
    """
    Convert seconds to MM:SS format.
    
    Args:
        seconds: Time in seconds
        
    Returns:
        Formatted timestamp string (MM:SS)
    """
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}:{secs:02d}"


def format_timestamp_ms(seconds: float) -> str:
    """
    Convert seconds to MM:SS.mmm format with milliseconds.
    
    Args:
        seconds: Time in seconds
        
    Returns:
        Formatted timestamp string (MM:SS.mmm)
    """
    minutes = int(seconds // 60)
    secs = seconds % 60
    return f"{minutes:02d}:{secs:06.3f}"


def get_duration(audio_length: int, sample_rate: int) -> float:
    """
    Calculate audio duration in seconds.
    
    Args:
        audio_length: Number of audio samples
        sample_rate: Sample rate in Hz
        
    Returns:
        Duration in seconds
    """
    return audio_length / sample_rate


def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """
    Setup logging configuration.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        
    Returns:
        Configured logger instance
    """
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    return logging.getLogger("multilingual-transcriber")


def create_output_directory(base_path: str = "./output") -> Path:
    """
    Create timestamped output directory.
    
    Args:
        base_path: Base directory path
        
    Returns:
        Path object for created directory
    """
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    output_dir = Path(base_path) / timestamp
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def seconds_to_readable(seconds: float) -> str:
    """
    Convert seconds to human-readable format.
    
    Args:
        seconds: Time in seconds
        
    Returns:
        Human-readable string (e.g., "1m 15s")
    """
    if seconds < 60:
        return f"{int(seconds)}s"
    
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    
    if minutes < 60:
        return f"{minutes}m {secs}s"
    
    hours = minutes // 60
    minutes = minutes % 60
    return f"{hours}h {minutes}m {secs}s"
