"""Output formatting module - generates JSON and Markdown files."""

import json
from pathlib import Path
from typing import List, Dict
from datetime import datetime
from rich.console import Console

console = Console()


def save_json(
    segments: List[Dict],
    output_path: str,
    metadata: Dict = None
) -> None:
    """
    Save transcription and translation to JSON file.
    
    Args:
        segments: List of processed segments with translations
        output_path: Path to save JSON file
        metadata: Additional metadata to include
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Calculate metadata
    if segments:
        total_duration = max(seg["end"] for seg in segments)
        unique_speakers = len(set(seg["speaker"] for seg in segments))
        lang_code = segments[0].get("lang", "unknown")
    else:
        total_duration = 0
        unique_speakers = 0
        lang_code = "unknown"
    
    # Build output structure
    output_data = {
        "metadata": {
            "language": lang_code,
            "speakers": unique_speakers,
            "duration": round(total_duration, 2),
            "total_segments": len(segments),
            "timestamp": datetime.now().isoformat(),
            **(metadata or {})
        },
        "segments": segments
    }
    
    # Write JSON
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    console.print(f"✓ Saved JSON: {output_path}", style="green")


def save_markdown(
    segments: List[Dict],
    output_path: str,
    metadata: Dict = None
) -> None:
    """
    Save transcription and translation to formatted Markdown file.
    
    Args:
        segments: List of processed segments with translations
        output_path: Path to save Markdown file
        metadata: Additional metadata to include
    """
    from utils.helpers import format_timestamp, get_duration
    from models.config import get_language_name
    
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Calculate metadata
    if segments:
        total_duration = max(seg["end"] for seg in segments)
        unique_speakers = len(set(seg["speaker"] for seg in segments))
        lang_code = segments[0].get("lang", "unknown")
        lang_name = get_language_name(lang_code)
    else:
        total_duration = 0
        unique_speakers = 0
        lang_code = "unknown"
        lang_name = "Unknown"
    
    # Build Markdown content
    lines = []
    
    # Header
    lines.append("# Audio Transcription & Translation")
    lines.append("")
    lines.append(f"**Language:** {lang_name} ({lang_code}) | "
                 f"**Speakers:** {unique_speakers} | "
                 f"**Duration:** {format_timestamp(total_duration)}")
    lines.append("")
    lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # Group segments by speaker for better readability
    current_speaker = None
    
    for seg in segments:
        speaker = seg["speaker"]
        start = seg["start"]
        end = seg["end"]
        original = seg["original"]
        english = seg.get("english", original)
        
        # Add speaker heading if changed
        if speaker != current_speaker:
            lines.append("")
            lines.append(f"## {speaker}")
            lines.append("")
            current_speaker = speaker
        
        # Add timestamp and text
        timestamp = f"**[{format_timestamp(start)}-{format_timestamp(end)}]**"
        
        # Original text
        lines.append(f"{timestamp} {original}")
        
        # English translation (if different from original)
        if english != original and lang_code.lower() not in ["en", "eng"]:
            lines.append(f"**EN:** {english}")
        
        lines.append("")
    
    # Write Markdown
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    
    console.print(f"✓ Saved Markdown: {output_path}", style="green")


def save_text(
    segments: List[Dict],
    output_path: str,
    include_timestamps: bool = True,
    include_speakers: bool = True
) -> None:
    """
    Save transcription to plain text file.
    
    Args:
        segments: List of processed segments
        output_path: Path to save text file
        include_timestamps: Whether to include timestamps
        include_speakers: Whether to include speaker labels
    """
    from utils.helpers import format_timestamp
    
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    lines = []
    
    for seg in segments:
        parts = []
        
        if include_speakers:
            parts.append(f"{seg['speaker']}:")
        
        if include_timestamps:
            parts.append(f"[{format_timestamp(seg['start'])}-{format_timestamp(seg['end'])}]")
        
        parts.append(seg["original"])
        
        lines.append(" ".join(parts))
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    
    console.print(f"✓ Saved text: {output_path}", style="green")


def save_srt(
    segments: List[Dict],
    output_path: str,
    use_translation: bool = False
) -> None:
    """
    Save transcription to SRT subtitle format.
    
    Args:
        segments: List of processed segments
        output_path: Path to save SRT file
        use_translation: Whether to use English translation instead of original
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    lines = []
    
    for i, seg in enumerate(segments, 1):
        # Subtitle index
        lines.append(str(i))
        
        # Timestamp in SRT format (HH:MM:SS,mmm --> HH:MM:SS,mmm)
        start_time = format_srt_timestamp(seg["start"])
        end_time = format_srt_timestamp(seg["end"])
        lines.append(f"{start_time} --> {end_time}")
        
        # Text (with speaker label)
        text = seg.get("english", seg["original"]) if use_translation else seg["original"]
        lines.append(f"{seg['speaker']}: {text}")
        
        # Empty line
        lines.append("")
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    
    console.print(f"✓ Saved SRT: {output_path}", style="green")


def format_srt_timestamp(seconds: float) -> str:
    """
    Convert seconds to SRT timestamp format (HH:MM:SS,mmm).
    
    Args:
        seconds: Time in seconds
        
    Returns:
        SRT formatted timestamp
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def save_all_formats(
    segments: List[Dict],
    output_dir: str,
    base_name: str = "result",
    metadata: Dict = None
) -> Dict[str, str]:
    """
    Save output in all formats (JSON, Markdown, Text, SRT).
    
    Args:
        segments: List of processed segments
        output_dir: Output directory path
        base_name: Base name for output files
        metadata: Additional metadata
        
    Returns:
        Dictionary mapping format to file path
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    files = {}
    
    # JSON
    json_path = output_dir / f"{base_name}.json"
    save_json(segments, json_path, metadata)
    files["json"] = str(json_path)
    
    # Markdown
    md_path = output_dir / f"{base_name}.md"
    save_markdown(segments, md_path, metadata)
    files["markdown"] = str(md_path)
    
    # Plain text
    txt_path = output_dir / f"{base_name}.txt"
    save_text(segments, txt_path)
    files["text"] = str(txt_path)
    
    # SRT (original)
    srt_path = output_dir / f"{base_name}_original.srt"
    save_srt(segments, srt_path, use_translation=False)
    files["srt_original"] = str(srt_path)
    
    # SRT (English)
    if segments and segments[0].get("lang", "en").lower() not in ["en", "eng"]:
        srt_en_path = output_dir / f"{base_name}_english.srt"
        save_srt(segments, srt_en_path, use_translation=True)
        files["srt_english"] = str(srt_en_path)
    
    return files
