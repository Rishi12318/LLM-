"""
FastAPI Backend for Multilingual Transcription
"""

import os
import sys
import shutil
from pathlib import Path
from typing import Optional
from datetime import datetime
import json

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from pipeline import (
    load_audio,
    whisper_transcribe,
    pyannote_diarize,
    align_segments,
    batch_translate,
)
from pipeline.format_output import save_all_formats
from models import ModelManager

app = FastAPI(title="Multilingual Transcriber API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directories
UPLOAD_DIR = Path(__file__).parent / "uploads"
RESULTS_DIR = Path(__file__).parent / "results"
UPLOAD_DIR.mkdir(exist_ok=True)
RESULTS_DIR.mkdir(exist_ok=True)

# Model manager (singleton)
model_manager = ModelManager()

# In-memory job storage (use Redis in production)
jobs = {}


class TranscriptionRequest(BaseModel):
    model: str = "large-v3"
    skip_diarization: bool = True
    min_speakers: Optional[int] = 1
    max_speakers: Optional[int] = None


class JobStatus(BaseModel):
    job_id: str
    status: str
    progress: int
    message: str
    result: Optional[dict] = None


@app.get("/")
async def root():
    """API health check"""
    return {
        "status": "online",
        "service": "Multilingual Transcriber API",
        "version": "1.0.0"
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    device = model_manager.get_device()
    return {
        "status": "healthy",
        "device": device,
        "timestamp": datetime.now().isoformat()
    }


@app.post("/transcribe")
async def transcribe_audio(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    model: str = "large-v3",
    skip_diarization: bool = True
):
    """
    Upload and transcribe audio file
    """
    # Validate file type
    if not file.filename:
        raise HTTPException(400, "No filename provided")
    
    ext = Path(file.filename).suffix.lower()
    if ext not in [".wav", ".mp3", ".m4a", ".flac", ".ogg", ".opus"]:
        raise HTTPException(400, f"Unsupported file type: {ext}")
    
    # Generate job ID
    job_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save uploaded file
    file_path = UPLOAD_DIR / f"{job_id}_{file.filename}"
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    
    # Initialize job status
    jobs[job_id] = {
        "status": "processing",
        "progress": 0,
        "message": "Audio uploaded, starting transcription...",
        "result": None,
        "filename": file.filename
    }
    
    # Process in background
    background_tasks.add_task(
        process_transcription,
        job_id,
        file_path,
        model,
        skip_diarization
    )
    
    return {
        "job_id": job_id,
        "status": "processing",
        "message": "Transcription started"
    }


async def process_transcription(
    job_id: str,
    file_path: Path,
    model: str,
    skip_diarization: bool
):
    """Background task to process transcription"""
    try:
        # Update status
        jobs[job_id]["progress"] = 10
        jobs[job_id]["message"] = "Loading audio..."
        
        # Load audio
        audio, sample_rate = load_audio(str(file_path))
        
        # Transcribe
        jobs[job_id]["progress"] = 30
        jobs[job_id]["message"] = "Transcribing audio..."
        
        lang_code, whisper_segments = whisper_transcribe(
            audio, sample_rate, model_name=model, device="auto"
        )
        
        # Diarization
        if not skip_diarization:
            jobs[job_id]["progress"] = 50
            jobs[job_id]["message"] = "Identifying speakers..."
            
            diar_segments = pyannote_diarize(audio, sample_rate, device="auto")
        else:
            diar_segments = []
        
        # Align
        jobs[job_id]["progress"] = 70
        jobs[job_id]["message"] = "Aligning segments..."
        
        aligned_segments = align_segments(whisper_segments, diar_segments, lang_code)
        
        # Translate
        jobs[job_id]["progress"] = 85
        jobs[job_id]["message"] = "Translating..."
        
        translated_segments = batch_translate(aligned_segments, lang_code)
        
        # Save results
        jobs[job_id]["progress"] = 95
        jobs[job_id]["message"] = "Saving results..."
        
        output_dir = RESULTS_DIR / job_id
        output_dir.mkdir(exist_ok=True)
        
        metadata = {
            "source_file": jobs[job_id]["filename"],
            "model": model,
            "language": lang_code,
        }
        
        saved_files = save_all_formats(
            translated_segments,
            str(output_dir),
            base_name="result",
            metadata=metadata
        )
        
        # Prepare result
        duration = max(seg["end"] for seg in translated_segments) if translated_segments else 0
        num_speakers = len(set(seg["speaker"] for seg in translated_segments))
        
        jobs[job_id]["status"] = "completed"
        jobs[job_id]["progress"] = 100
        jobs[job_id]["message"] = "Transcription completed!"
        jobs[job_id]["result"] = {
            "language": lang_code,
            "duration": round(duration, 2),
            "speakers": num_speakers,
            "segments": translated_segments,
            "files": {
                "json": f"/results/{job_id}/result.json",
                "markdown": f"/results/{job_id}/result.md",
                "text": f"/results/{job_id}/result.txt",
                "srt": f"/results/{job_id}/result_original.srt"
            }
        }
        
        # Cleanup uploaded file
        file_path.unlink(missing_ok=True)
        
    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["progress"] = 0
        jobs[job_id]["message"] = f"Error: {str(e)}"
        jobs[job_id]["result"] = None


@app.get("/status/{job_id}")
async def get_job_status(job_id: str):
    """Get transcription job status"""
    if job_id not in jobs:
        raise HTTPException(404, "Job not found")
    
    return jobs[job_id]


@app.get("/results/{job_id}/{filename}")
async def get_result_file(job_id: str, filename: str):
    """Download result file"""
    file_path = RESULTS_DIR / job_id / filename
    
    if not file_path.exists():
        raise HTTPException(404, "File not found")
    
    return FileResponse(file_path)


@app.get("/jobs")
async def list_jobs():
    """List all jobs"""
    return {
        "jobs": [
            {
                "job_id": job_id,
                "status": job["status"],
                "filename": job.get("filename", "unknown"),
                "progress": job["progress"]
            }
            for job_id, job in jobs.items()
        ]
    }


@app.delete("/job/{job_id}")
async def delete_job(job_id: str):
    """Delete a job and its results"""
    if job_id not in jobs:
        raise HTTPException(404, "Job not found")
    
    # Delete result files
    result_dir = RESULTS_DIR / job_id
    if result_dir.exists():
        shutil.rmtree(result_dir)
    
    # Remove from jobs
    del jobs[job_id]
    
    return {"message": "Job deleted successfully"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
