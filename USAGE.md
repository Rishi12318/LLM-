# Quick Start Guide

## System is Now Running! 🚀

### Access the Application
Open your browser to: **http://localhost:3000**

### Servers Status
- ✅ **Backend API**: http://127.0.0.1:8000 (FastAPI)
- ✅ **Frontend**: http://localhost:3000 (Next.js)

## How to Use

### 1. Upload Audio File
- Visit http://localhost:3000
- Drag and drop an audio file (WAV, MP3, M4A, FLAC, OGG)
- Or click "Browse files" to select manually
- Maximum file size: 100MB

### 2. Wait for Processing
- Progress bar shows real-time status
- First run downloads models (~5GB, one-time)
- Processing time depends on audio length and hardware

### 3. Download Results
Once complete, download any format:
- **JSON**: Structured data with all metadata
- **Markdown**: Readable format with formatting
- **Text**: Simple transcript
- **SRT**: Subtitles for video players

## What Happens Behind the Scenes

```
1. Audio Upload → Backend receives file
2. Job Created → Unique ID assigned
3. Audio Loading → Converts to WAV 16kHz mono
4. Language Detection → Whisper identifies language
5. Transcription → Whisper Large V3 transcribes
6. Speaker Diarization → Pyannote identifies speakers
7. Alignment → Matches speakers to transcript segments
8. Translation → Helsinki-NLP translates to English
9. Output Generation → Creates JSON, MD, TXT, SRT files
10. Results Ready → Download links appear
```

## Testing with Sample Audio

Try with the existing sample:
```bash
# Copy sample to an easy location
copy C:\Users\rishi\OneDrive\Desktop\LLM\multilingual-transcriber\sample.wav C:\Users\rishi\Downloads\
```

Then upload `C:\Users\rishi\Downloads\sample.wav` through the web interface.

## API Testing (Optional)

You can also use the API directly:

### Interactive API Docs
Visit: http://127.0.0.1:8000/docs

### Upload via cURL
```bash
curl -X POST "http://127.0.0.1:8000/transcribe" \
  -F "file=@sample.wav"
```

### Check Status
```bash
curl "http://127.0.0.1:8000/status/{job_id}"
```

## Stopping the Servers

Press **CTRL+C** in each terminal window where the servers are running.

Or close the terminal windows entirely.

## Troubleshooting

### Frontend can't connect to backend
- Verify backend is running: http://127.0.0.1:8000/health
- Check browser console for CORS errors
- Ensure both servers are running in separate terminals

### Slow transcription
- First run downloads ~5GB models (10+ minutes on slow connection)
- CPU processing: ~3 minutes per 1 minute of audio
- GPU would be much faster (requires CUDA-enabled PyTorch)

### Out of memory
- Split large audio files into smaller chunks (< 10 minutes each)
- Close other memory-intensive applications
- Consider upgrading RAM (16GB+ recommended)

### Port already in use
Backend:
```bash
# Change port in backend/api.py or use different port:
python -m uvicorn api:app --reload --port 8001
```

Frontend:
```bash
# Next.js will auto-select next available port (3001, 3002, etc.)
npm run dev
```

## Performance Expectations

| Audio Length | CPU (i7) | GPU (RTX 3080) |
|--------------|----------|----------------|
| 30 seconds | ~15 sec | ~3 sec |
| 1 minute | ~30 sec | ~5 sec |
| 5 minutes | ~2.5 min | ~15 sec |
| 10 minutes | ~5 min | ~30 sec |

*Add ~10 minutes for first-time model downloads*

## What's Next?

### Enhance the System
- Add GPU support for faster processing
- Implement job queue for multiple uploads
- Add user authentication
- Store results in database
- Add support for video files
- Batch processing for multiple files

### Deploy to Production
- Use Docker containers
- Deploy backend to cloud (AWS, Azure, GCP)
- Deploy frontend to Vercel or Netlify
- Add CDN for faster model downloads
- Set up monitoring and logging

---

**Need Help?**
- Check http://127.0.0.1:8000/docs for API documentation
- Review logs in terminal windows
- Test CLI directly: `python main.py sample.wav`
