"""Translation module using Helsinki-NLP Opus-MT models."""

from typing import List, Dict
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
import torch

console = Console()


def batch_translate(
    segments: List[Dict],
    source_lang: str,
    target_lang: str = "en",
    batch_size: int = 8
) -> List[Dict]:
    """
    Translate all segments to English using Helsinki-NLP Opus-MT models.
    
    Args:
        segments: List of aligned segments with original text
            [{"speaker": "Speaker 1", "start": 0.0, "end": 2.5, 
              "original": "Bonjour", "lang": "fr"}]
        source_lang: Source language code (e.g., 'fr', 'es', 'de')
        target_lang: Target language code (default: 'en' for English)
        batch_size: Number of segments to translate at once
        
    Returns:
        Segments with added 'english' field
        [{"speaker": "Speaker 1", ..., "english": "Hello"}]
    """
    console.print("\n🌐 TRANSLATION", style="bold yellow")
    console.print("─" * 60)
    
    # If already in English, no translation needed
    if source_lang.lower() in ["en", "eng"]:
        console.print("✓ Source is English, skipping translation", style="green")
        for seg in segments:
            seg["english"] = seg["original"]
        return segments
    
    try:
        from transformers import pipeline
        from models.config import get_translation_model, get_language_name
        
        # Get appropriate translation model
        model_id = get_translation_model(source_lang, target_lang)
        
        if model_id is None:
            console.print("✓ No translation needed", style="green")
            for seg in segments:
                seg["english"] = seg["original"]
            return segments
        
        console.print(f"Loading translation model: {model_id}")
        console.print(f"Translating {get_language_name(source_lang)} → English")
        
        # Load translation pipeline
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Loading translator...", total=None)
            
            # Auto-detect device
            device = 0 if torch.cuda.is_available() else -1
            
            translator = pipeline(
                "translation",
                model=model_id,
                device=device
            )
            
            progress.update(task, completed=True)
        
        console.print("✓ Translator loaded", style="green")
        
        # Translate in batches with progress bar
        total_segments = len(segments)
        translated_segments = []
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console,
        ) as progress:
            task = progress.add_task("Translating...", total=total_segments)
            
            for i in range(0, total_segments, batch_size):
                batch = segments[i:i + batch_size]
                texts = [seg["original"] for seg in batch]
                
                # Translate batch
                translations = translator(texts, max_length=512)
                
                # Add translations to segments
                for j, seg in enumerate(batch):
                    seg_copy = seg.copy()
                    seg_copy["english"] = translations[j]["translation_text"]
                    translated_segments.append(seg_copy)
                
                progress.update(task, advance=len(batch))
        
        console.print(f"✓ Translated {total_segments} segments", style="green")
        
        # Show sample
        if translated_segments:
            sample = translated_segments[0]
            console.print(f'\nSample:', style="dim")
            console.print(f'  Original: "{sample["original"][:80]}..."', style="dim")
            console.print(f'  English:  "{sample["english"][:80]}..."', style="dim")
        
        return translated_segments
        
    except ImportError as e:
        console.print(f"❌ Translation dependencies missing: {e}", style="red")
        console.print("   Install with: pip install transformers sentencepiece", style="yellow")
        # Return segments without translation
        for seg in segments:
            seg["english"] = seg["original"]
        return segments
        
    except Exception as e:
        console.print(f"❌ Translation failed: {e}", style="red")
        console.print("⚠️  Continuing without translation", style="yellow")
        # Return segments without translation
        for seg in segments:
            seg["english"] = seg.get("original", "")
        return segments


def translate_text(
    text: str,
    source_lang: str,
    target_lang: str = "en"
) -> str:
    """
    Translate a single text string.
    
    Args:
        text: Text to translate
        source_lang: Source language code
        target_lang: Target language code (default: 'en' for English)
        
    Returns:
        Translated text
    """
    try:
        from transformers import pipeline
        from models.config import get_translation_model
        
        if source_lang.lower() in ["en", "eng"]:
            return text
        
        model_id = get_translation_model(source_lang)
        if model_id is None:
            return text
        
        device = 0 if torch.cuda.is_available() else -1
        translator = pipeline("translation", model=model_id, device=device)
        
        result = translator(text, max_length=512)
        return result[0]["translation_text"]
        
    except Exception as e:
        console.print(f"⚠️  Translation error: {e}", style="yellow")
        return text


def get_supported_languages() -> List[str]:
    """
    Get list of supported source languages for translation.
    
    Returns:
        List of ISO 639-1 language codes
    """
    from models.config import OPUS_MT_MODELS
    return list(OPUS_MT_MODELS.keys())


def validate_language_support(lang_code: str) -> bool:
    """
    Check if a language is supported for translation.
    
    Args:
        lang_code: ISO 639-1 language code
        
    Returns:
        True if supported, False otherwise
    """
    if lang_code.lower() in ["en", "eng"]:
        return True
    
    from models.config import get_translation_model
    model = get_translation_model(lang_code)
    return model is not None
