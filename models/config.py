"""Model configuration and names."""

from typing import Dict

# Whisper model configurations
WHISPER_MODELS = {
    "tiny": "openai/whisper-tiny",
    "base": "openai/whisper-base",
    "small": "openai/whisper-small",
    "medium": "openai/whisper-medium",
    "large": "openai/whisper-large-v2",
    "large-v3": "openai/whisper-large-v3",
}

# Default Whisper model
DEFAULT_WHISPER_MODEL = "large-v3"

# Pyannote speaker diarization model
PYANNOTE_MODEL = "pyannote/speaker-diarization-3.1"

# Helsinki-NLP translation models (language code to model mapping)
OPUS_MT_MODELS = {
    "ar": "Helsinki-NLP/opus-mt-ar-en",      # Arabic
    "zh": "Helsinki-NLP/opus-mt-zh-en",      # Chinese
    "nl": "Helsinki-NLP/opus-mt-nl-en",      # Dutch
    "fr": "Helsinki-NLP/opus-mt-fr-en",      # French
    "de": "Helsinki-NLP/opus-mt-de-en",      # German
    "el": "Helsinki-NLP/opus-mt-el-en",      # Greek
    "hi": "Helsinki-NLP/opus-mt-hi-en",      # Hindi
    "id": "Helsinki-NLP/opus-mt-id-en",      # Indonesian
    "it": "Helsinki-NLP/opus-mt-it-en",      # Italian
    "ja": "Helsinki-NLP/opus-mt-ja-en",      # Japanese
    "ko": "Helsinki-NLP/opus-mt-ko-en",      # Korean
    "ms": "Helsinki-NLP/opus-mt-ms-en",      # Malay
    "fa": "Helsinki-NLP/opus-mt-fa-en",      # Persian
    "pl": "Helsinki-NLP/opus-mt-pl-en",      # Polish
    "pt": "Helsinki-NLP/opus-mt-pt-en",      # Portuguese
    "ru": "Helsinki-NLP/opus-mt-ru-en",      # Russian
    "es": "Helsinki-NLP/opus-mt-es-en",      # Spanish
    "sv": "Helsinki-NLP/opus-mt-sv-en",      # Swedish
    "ta": "Helsinki-NLP/opus-mt-ta-en",      # Tamil
    "te": "Helsinki-NLP/opus-mt-te-en",      # Telugu
    "th": "Helsinki-NLP/opus-mt-th-en",      # Thai
    "tr": "Helsinki-NLP/opus-mt-tr-en",      # Turkish
    "uk": "Helsinki-NLP/opus-mt-uk-en",      # Ukrainian
    "ur": "Helsinki-NLP/opus-mt-ur-en",      # Urdu
    "vi": "Helsinki-NLP/opus-mt-vi-en",      # Vietnamese
}

# Fallback multi-language translation model (covers 50+ languages)
OPUS_MT_FALLBACK = "Helsinki-NLP/opus-mt-mul-en"

# Model configuration dictionary
MODEL_CONFIG: Dict[str, str] = {
    "whisper": WHISPER_MODELS[DEFAULT_WHISPER_MODEL],
    "diarization": PYANNOTE_MODEL,
    "translation_fallback": OPUS_MT_FALLBACK,
}


def get_translation_model(lang_code: str, target_lang: str = "en") -> str:
    """
    Get the appropriate translation model for a given language code.
    
    Args:
        lang_code: ISO 639-1 language code (e.g., 'hi', 'fr', 'es')
        target_lang: Target language (default: 'en')
        
    Returns:
        HuggingFace model ID for translation
    """
    # If already English, no translation needed
    if lang_code.lower() in ["en", "eng"]:
        return None
    
    # Check if specific model exists
    if lang_code.lower() in OPUS_MT_MODELS:
        return OPUS_MT_MODELS[lang_code.lower()]
    
    # Return fallback model for other languages
    return OPUS_MT_FALLBACK


# Language name mapping (for display purposes)
LANGUAGE_NAMES = {
    "en": "English",
    "hi": "Hindi",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "it": "Italian",
    "pt": "Portuguese",
    "ru": "Russian",
    "ja": "Japanese",
    "ko": "Korean",
    "zh": "Chinese",
    "ar": "Arabic",
    "ta": "Tamil",
    "te": "Telugu",
    "ur": "Urdu",
    "tr": "Turkish",
    "nl": "Dutch",
    "pl": "Polish",
    "sv": "Swedish",
    "vi": "Vietnamese",
    "th": "Thai",
    "id": "Indonesian",
    "ms": "Malay",
    "fa": "Persian",
    "el": "Greek",
    "uk": "Ukrainian",
}


def get_language_name(lang_code: str) -> str:
    """
    Get the full language name from ISO code.
    
    Args:
        lang_code: ISO 639-1 language code
        
    Returns:
        Full language name or the code if not found
    """
    return LANGUAGE_NAMES.get(lang_code.lower(), lang_code.upper())
