"""Segment alignment module - matches transcription with speaker diarization."""

from typing import List, Dict
from rich.console import Console

console = Console()


def align_segments(
    whisper_segments: List[Dict],
    diarization_segments: List[Dict],
    lang_code: str,
    overlap_threshold: float = 0.5
) -> List[Dict]:
    """
    Align Whisper transcription segments with speaker diarization.
    
    Matches each transcribed text segment with the corresponding speaker
    based on temporal overlap.
    
    Args:
        whisper_segments: List of transcription segments
            [{"start": 0.0, "end": 2.5, "text": "Hello"}]
        diarization_segments: List of speaker segments
            [{"start": 0.0, "end": 2.5, "speaker": "SPEAKER_00"}]
        lang_code: ISO 639-1 language code
        overlap_threshold: Minimum overlap ratio to assign speaker (0.0-1.0)
        
    Returns:
        List of aligned segments with speaker labels
        [{"speaker": "Speaker 1", "start": 0.0, "end": 2.5, 
          "original": "Hello", "lang": "en"}]
    """
    console.print("\n🔗 ALIGNING SPEAKERS & TEXT", style="bold yellow")
    console.print("─" * 60)
    
    if not diarization_segments:
        console.print("⚠️  No diarization data, assigning default speaker", style="yellow")
        # Assign all to "Speaker 1" if no diarization
        aligned = []
        for seg in whisper_segments:
            aligned.append({
                "speaker": "Speaker 1",
                "start": seg["start"],
                "end": seg["end"],
                "original": seg["text"],
                "lang": lang_code
            })
        return aligned
    
    # Rename speakers first (SPEAKER_00 -> Speaker 1)
    from .pyannote_diar import rename_speakers
    diarization_segments = rename_speakers(diarization_segments)
    
    aligned = []
    
    for whisper_seg in whisper_segments:
        w_start = whisper_seg["start"]
        w_end = whisper_seg["end"]
        w_duration = w_end - w_start
        
        # Find best matching speaker based on overlap
        best_speaker = "Speaker 1"  # Default
        max_overlap = 0.0
        
        for diar_seg in diarization_segments:
            d_start = diar_seg["start"]
            d_end = diar_seg["end"]
            
            # Calculate overlap
            overlap_start = max(w_start, d_start)
            overlap_end = min(w_end, d_end)
            overlap_duration = max(0, overlap_end - overlap_start)
            
            # Calculate overlap ratio
            if w_duration > 0:
                overlap_ratio = overlap_duration / w_duration
                
                if overlap_ratio > max_overlap:
                    max_overlap = overlap_ratio
                    best_speaker = diar_seg["speaker"]
        
        # Only assign speaker if overlap is significant
        if max_overlap < overlap_threshold:
            # Try to find nearest speaker if no good overlap
            best_speaker = find_nearest_speaker(w_start, w_end, diarization_segments)
        
        aligned.append({
            "speaker": best_speaker,
            "start": w_start,
            "end": w_end,
            "original": whisper_seg["text"],
            "lang": lang_code
        })
    
    # Group consecutive segments by speaker for cleaner output
    aligned = merge_consecutive_speaker_segments(aligned)
    
    # Count speakers
    unique_speakers = len(set(seg["speaker"] for seg in aligned))
    console.print(f"✓ Aligned {len(aligned)} segments with {unique_speakers} speaker(s)", style="green")
    
    return aligned


def find_nearest_speaker(start: float, end: float, diar_segments: List[Dict]) -> str:
    """
    Find the nearest speaker segment to a given time range.
    
    Args:
        start: Start time
        end: End time
        diar_segments: List of speaker segments
        
    Returns:
        Speaker label
    """
    if not diar_segments:
        return "Speaker 1"
    
    midpoint = (start + end) / 2
    min_distance = float("inf")
    nearest_speaker = diar_segments[0]["speaker"]
    
    for seg in diar_segments:
        seg_midpoint = (seg["start"] + seg["end"]) / 2
        distance = abs(midpoint - seg_midpoint)
        
        if distance < min_distance:
            min_distance = distance
            nearest_speaker = seg["speaker"]
    
    return nearest_speaker


def merge_consecutive_speaker_segments(segments: List[Dict]) -> List[Dict]:
    """
    Merge consecutive segments from the same speaker that are close together.
    
    Args:
        segments: List of aligned segments
        
    Returns:
        Merged list of segments
    """
    if not segments:
        return []
    
    merged = []
    current = segments[0].copy()
    
    for seg in segments[1:]:
        # If same speaker and within 1 second gap, merge
        if (seg["speaker"] == current["speaker"] and 
            seg["start"] - current["end"] <= 1.0):
            current["end"] = seg["end"]
            current["original"] += " " + seg["original"]
        else:
            merged.append(current)
            current = seg.copy()
    
    merged.append(current)
    return merged


def calculate_overlap(start1: float, end1: float, start2: float, end2: float) -> float:
    """
    Calculate temporal overlap between two segments.
    
    Args:
        start1, end1: First segment times
        start2, end2: Second segment times
        
    Returns:
        Overlap duration in seconds
    """
    overlap_start = max(start1, start2)
    overlap_end = min(end1, end2)
    return max(0, overlap_end - overlap_start)


def get_alignment_quality_score(aligned: List[Dict], diarization: List[Dict]) -> float:
    """
    Calculate quality score for alignment (0.0 to 1.0).
    
    Args:
        aligned: Aligned segments
        diarization: Original diarization segments
        
    Returns:
        Quality score (higher is better)
    """
    if not aligned or not diarization:
        return 0.0
    
    total_overlap = 0.0
    total_duration = 0.0
    
    for aligned_seg in aligned:
        seg_duration = aligned_seg["end"] - aligned_seg["start"]
        total_duration += seg_duration
        
        # Find best matching diarization segment
        best_overlap = 0.0
        for diar_seg in diarization:
            if diar_seg["speaker"] == aligned_seg["speaker"]:
                overlap = calculate_overlap(
                    aligned_seg["start"], aligned_seg["end"],
                    diar_seg["start"], diar_seg["end"]
                )
                best_overlap = max(best_overlap, overlap)
        
        total_overlap += best_overlap
    
    return total_overlap / total_duration if total_duration > 0 else 0.0
