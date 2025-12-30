@echo off
cd backend
echo Starting FastAPI Backend on http://localhost:8000...
uvicorn api:app --reload --host 0.0.0.0 --port 8000
