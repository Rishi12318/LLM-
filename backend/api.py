"""
FastAPI Backend for Multilingual Transcription
"""

import json
import logging
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import APIRouter, BackgroundTasks, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.rag import EvaluationCase, RAGService, SAMPLE_EVALUATION_CASES, get_default_generator
from models import ModelManager
from pipeline import align_segments, batch_translate, load_audio, pyannote_diarize, whisper_transcribe
from pipeline.format_output import save_all_formats
from utils.helpers import setup_logging

app = FastAPI(title="Multilingual Transcriber API", version="2.0.0")
logger = setup_logging(os.getenv("LOG_LEVEL", "INFO"))
api_router = APIRouter(prefix="/api")

# Configure CORS origins for local and deployed frontends
default_origins = ["http://localhost:3000", "http://localhost:3001"]
env_origins = [origin.strip() for origin in os.getenv("CORS_ORIGINS", "").split(",") if origin.strip()]
frontend_url = os.getenv("FRONTEND_URL", "").strip()
allow_origins = sorted(set(default_origins + env_origins + ([frontend_url] if frontend_url else [])))

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directories
UPLOAD_DIR = Path(__file__).parent / "uploads"
RESULTS_DIR = Path(__file__).parent / "results"
STORAGE_DIR = Path(__file__).parent / "storage"
FRONTEND_DIST_DIR = Path(os.getenv("FRONTEND_DIST_DIR", str(Path(__file__).parent.parent / "frontend" / "out")))
UPLOAD_DIR.mkdir(exist_ok=True)
RESULTS_DIR.mkdir(exist_ok=True)
STORAGE_DIR.mkdir(exist_ok=True)

# Model manager (singleton)
model_manager = ModelManager()
rag_service = RAGService(STORAGE_DIR)

# Initialize LLM generator (Ollama if available, else context-only fallback)
try:
    rag_generator = get_default_generator(prefer_ollama=True)
    logger.info(f"RAG generator initialized: {rag_generator.__class__.__name__}")
except Exception as e:
    logger.warning(f"Error initializing RAG generator, using fallback: {e}")
    from backend.rag import SimpleContextGenerator
    rag_generator = SimpleContextGenerator()

# In-memory job storage (use Redis in production)
jobs: Dict[str, Dict[str, Any]] = {}


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


class RagIngestRequest(BaseModel):
    document_id: Optional[str] = None
    source_name: str
    text: str = Field(..., min_length=1)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class RagQueryRequest(BaseModel):
    question: str = Field(..., min_length=1)
    top_k: int = Field(default=5, ge=1, le=20)
    use_llm: bool = Field(default=True, description="Use LLM generator if available, else context-only")
    history: Optional[List[Dict[str, str]]] = Field(default=None, description="Conversation history (list of role/content dicts)")


class RagEvaluationRequest(BaseModel):
    cases: Optional[list[dict[str, Any]]] = None


@api_router.get("/health")
async def health():
    """Health check endpoint"""
    device = model_manager.get_device()
    return {
        "status": "healthy",
        "device": device,
        "timestamp": datetime.now().isoformat(),
        "rag_index": rag_service.vector_store.stats(),
    }


@api_router.post("/transcribe")
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


@api_router.post("/rag/ingest")
async def ingest_rag_document(request: RagIngestRequest):
    """Ingest a document into the retrieval index."""
    document_id = request.document_id or request.source_name.replace(" ", "-").lower()
    record = rag_service.ingest_text(
        document_id=document_id,
        source_name=request.source_name,
        text=request.text,
        metadata=request.metadata,
    )
    return {"status": "ok", "document": record, "index": rag_service.vector_store.stats()}


@api_router.post("/rag/query")
async def query_rag(request: RagQueryRequest):
    """Query the retrieval index and return a grounded prompt + answer draft.
    
    Args:
        request.question: Query text
        request.top_k: Number of context chunks to retrieve
        request.use_llm: If true, use LLM generator; if false, return context only
        
    Returns:
        answer: LLM-generated (or context summary) grounded answer
        messages: Structured prompt messages sent to LLM
        retrieval: Context chunks with metadata
        validation: Groundedness checks (citations, hallucination risk)
    """
    generator = rag_generator if request.use_llm else None
    try:
        return rag_service.query(
            request.question, 
            top_k=request.top_k, 
            generator=generator,
            history=request.history
        )
    except RuntimeError as e:
        logger.error(f"RAG query failed: {e}")
        # Fallback: return context-only answer
        return rag_service.query(request.question, top_k=request.top_k, generator=None)


@api_router.post("/rag/evaluate")
async def evaluate_rag(request: RagEvaluationRequest):
    """Run the sample or custom evaluation suite."""
    if request.cases:
        cases = [EvaluationCase(**case) for case in request.cases]
    else:
        cases = SAMPLE_EVALUATION_CASES
    return rag_service.evaluate(cases)


@api_router.get("/summarize/{job_id}")
async def summarize_transcript(job_id: str):
    """Generate a summary for a specific transcription job."""
    if job_id not in jobs:
        # Check if job exists in results directory
        job_dir = RESULTS_DIR / job_id
        if not job_dir.exists():
            raise HTTPException(404, "Job not found")
        
        # Load result.json to get segments
        result_file = job_dir / "result.json"
        if not result_file.exists():
            raise HTTPException(404, "Result file not found")
        
        with open(result_file, "r", encoding="utf-8") as f:
            result_data = json.load(f)
            segments = result_data.get("segments", [])
    else:
        job = jobs[job_id]
        if job["status"] != "completed":
            raise HTTPException(400, f"Job is in status: {job['status']}")
        segments = job["result"].get("segments", [])

    if not segments:
        raise HTTPException(400, "No transcription segments found to summarize.")

    # Convert segments to text
    from backend.rag.chunking import transcript_segments_to_text
    text = transcript_segments_to_text(segments)
    
    # Generate summary
    summary = rag_service.summarize(text, generator=rag_generator)
    
    return {"job_id": job_id, "summary": summary}


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
        jobs[job_id]["message"] = "Translating to English..."
        
        translated_segments = batch_translate(aligned_segments, lang_code, target_lang="en")
        
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

        # Index the transcript so the retrieval layer can ground future questions.
        try:
            rag_service.ingest_transcription(
                job_id,
                translated_segments,
                metadata={
                    **metadata,
                    "output_dir": str(output_dir),
                    "saved_files": saved_files,
                },
            )
        except Exception:
            logger.exception("RAG indexing failed for job %s", job_id)

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
        logger.info("Completed transcription job %s", job_id)
        
    except Exception as e:
        logger.exception("Transcription job %s failed", job_id)
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["progress"] = 0
        jobs[job_id]["message"] = f"Error: {str(e)}"
        jobs[job_id]["result"] = None


@api_router.get("/status/{job_id}")
async def get_job_status(job_id: str):
    """Get transcription job status"""
    if job_id not in jobs:
        raise HTTPException(404, "Job not found")
    
    return jobs[job_id]


@api_router.get("/results/{job_id}/{filename}")
async def get_result_file(job_id: str, filename: str):
    """Download result file"""
    file_path = RESULTS_DIR / job_id / filename
    
    if not file_path.exists():
        raise HTTPException(404, "File not found")
    
    return FileResponse(file_path)


@api_router.get("/jobs")
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


@api_router.delete("/job/{job_id}")
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


app.include_router(api_router)

if FRONTEND_DIST_DIR.exists():
    app.mount("/", StaticFiles(directory=FRONTEND_DIST_DIR, html=True), name="frontend")
else:
    @app.get("/")
    async def root():
        return {
            "status": "online",
            "service": "Multilingual Transcriber API",
            "version": "1.0.0",
            "frontend": "not-built"
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
