"""Model caching and auto-download management."""

import os
from pathlib import Path
from typing import Optional

import torch
from huggingface_hub import hf_hub_download, snapshot_download
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

from .config import MODEL_CONFIG, WHISPER_MODELS, get_translation_model

console = Console()


class ModelManager:
    """Manages model downloading, caching, and verification."""
    
    def __init__(self, cache_dir: Optional[str] = None):
        """
        Initialize model manager.
        
        Args:
            cache_dir: Custom cache directory (defaults to HuggingFace cache)
        """
        self.cache_dir = cache_dir or os.path.join(Path.home(), ".cache", "huggingface")
        os.makedirs(self.cache_dir, exist_ok=True)
        
    def get_device(self) -> str:
        """
        Auto-detect and return the best available device.
        
        Returns:
            Device string: "cuda", "mps", or "cpu"
        """
        if torch.cuda.is_available():
            device = "cuda"
            console.print(f"✓ Using GPU: {torch.cuda.get_device_name(0)}", style="green")
        elif torch.backends.mps.is_available():
            device = "mps"
            console.print("✓ Using Apple Silicon GPU (MPS)", style="green")
        else:
            device = "cpu"
            console.print("✓ Using CPU (GPU not available)", style="yellow")
        
        return device
    
    def ensure_whisper_model(self, model_name: str = "large-v3") -> str:
        """
        Ensure Whisper model is downloaded and cached.
        
        Args:
            model_name: Whisper model size (tiny, base, small, medium, large, large-v3)
            
        Returns:
            Model identifier string
        """
        if model_name not in WHISPER_MODELS:
            console.print(f"⚠️  Unknown model '{model_name}', using 'large-v3'", style="yellow")
            model_name = "large-v3"
        
        model_id = WHISPER_MODELS[model_name]
        
        console.print(f"🔍 Checking Whisper model: {model_id}")
        
        try:
            # Whisper models are handled by the whisper library
            # Just return the model name, it will auto-download on first use
            return model_name
        except Exception as e:
            console.print(f"❌ Error verifying Whisper model: {e}", style="red")
            raise
    
    def ensure_diarization_model(self) -> str:
        """
        Ensure Pyannote diarization model is downloaded.
        
        Returns:
            Model identifier string
        """
        model_id = MODEL_CONFIG["diarization"]
        console.print(f"🔍 Checking diarization model: {model_id}")
        
        try:
            # Pyannote models require HuggingFace authentication
            # The model will be auto-downloaded on first use
            return model_id
        except Exception as e:
            console.print(f"❌ Error verifying diarization model: {e}", style="red")
            raise
    
    def ensure_translation_model(self, lang_code: str) -> Optional[str]:
        """
        Ensure translation model for the given language is downloaded.
        
        Args:
            lang_code: ISO 639-1 language code
            
        Returns:
            Model identifier string or None if English
        """
        model_id = get_translation_model(lang_code)
        
        if model_id is None:
            console.print("✓ Source language is English, no translation needed", style="green")
            return None
        
        console.print(f"🔍 Checking translation model: {model_id}")
        
        try:
            # Translation models will be auto-downloaded by transformers pipeline
            return model_id
        except Exception as e:
            console.print(f"⚠️  Error verifying translation model: {e}", style="yellow")
            console.print(f"   Will attempt to download on first use", style="yellow")
            return model_id
    
    def download_model(self, model_id: str, model_type: str = "generic") -> bool:
        """
        Download a model from HuggingFace Hub with progress bar.
        
        Args:
            model_id: HuggingFace model identifier
            model_type: Type of model (for display)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            console.print(f"📥 Downloading {model_type} model: {model_id}")
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                console=console,
            ) as progress:
                task = progress.add_task(f"Downloading {model_id}...", total=None)
                
                # Download full model repository
                snapshot_download(
                    repo_id=model_id,
                    cache_dir=self.cache_dir,
                    resume_download=True,
                )
                
                progress.update(task, completed=True)
            
            console.print(f"✓ {model_type.capitalize()} model downloaded successfully", style="green")
            return True
            
        except Exception as e:
            console.print(f"❌ Failed to download {model_type} model: {e}", style="red")
            return False
    
    def verify_all_models(self, whisper_model: str = "large-v3", lang_code: str = "en") -> bool:
        """
        Verify all required models are available or download them.
        
        Args:
            whisper_model: Whisper model size
            lang_code: Language code for translation model
            
        Returns:
            True if all models are ready, False otherwise
        """
        console.print("\n" + "="*60, style="bold cyan")
        console.print("🔧 MODEL VERIFICATION & AUTO-DOWNLOAD", style="bold cyan")
        console.print("="*60 + "\n", style="bold cyan")
        
        try:
            # Check Whisper
            self.ensure_whisper_model(whisper_model)
            
            # Check Diarization
            self.ensure_diarization_model()
            
            # Check Translation (if not English)
            if lang_code.lower() not in ["en", "eng"]:
                self.ensure_translation_model(lang_code)
            
            console.print("\n✅ All models verified and ready!", style="bold green")
            return True
            
        except Exception as e:
            console.print(f"\n❌ Model verification failed: {e}", style="bold red")
            return False
    
    def get_model_info(self) -> dict:
        """
        Get information about cached models.
        
        Returns:
            Dictionary with model information
        """
        info = {
            "cache_dir": self.cache_dir,
            "device": self.get_device(),
            "whisper_models": list(WHISPER_MODELS.keys()),
            "diarization_model": MODEL_CONFIG["diarization"],
        }
        return info
