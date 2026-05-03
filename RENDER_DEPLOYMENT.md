# 🚀 Deploy to Render - Complete Guide

This guide walks you through deploying the Multilingual Transcriber with Ollama integration to Render.

## 📋 Prerequisites

- [Render account](https://render.com) (free tier available)
- GitHub account with this repository
- Git configured locally

## 🎯 What We're Deploying

- **Backend**: FastAPI application on Render Web Service
- **Frontend**: Next.js application on Render Web Service  
- **Database**: Optional PostgreSQL (for production features)
- **Ollama**: Optional (can run locally or on separate GPU instance)

## 🔄 Deployment Architecture

```
GitHub Repository
       ↓
   (Push code)
       ↓
Render (connected to GitHub)
       ↓
   ├─ Backend (Port 8000)
   ├─ Frontend (Port 3000)
   └─ Ollama (Optional, Port 11434)
```

## 📝 Step-by-Step Deployment

### 1️⃣ **Create Render Account**
1. Go to [render.com](https://render.com)
2. Sign up with GitHub account
3. Authorize Render to access your repositories

### 2️⃣ **Connect Repository**
1. In Render Dashboard → "New +"
2. Select "Web Service"
3. Connect your GitHub repository
4. Choose branch: `master`

### 3️⃣ **Deploy Backend Service**

**Create Web Service for Backend:**
1. Go to Render Dashboard → New → Web Service
2. Configure:
   - **Name**: `multilingual-transcriber-backend`
   - **Runtime**: Python 3.11
   - **Build Command**:
     ```bash
     pip install -r requirements.txt && pip install -r backend/requirements.txt
     ```
   - **Start Command**:
     ```bash
     python -m uvicorn backend.api:app --host 0.0.0.0 --port $PORT
     ```
   - **Plan**: Free or Paid (Standard for production)

3. **Environment Variables**:
   - `PYTHON_VERSION`: 3.11
   - `LOG_LEVEL`: INFO
   - `OLLAMA_HOST`: http://localhost:11434 (or Ollama service URL if separate)

4. Click "Deploy"

**Get Backend URL:**
- After deployment: `https://multilingual-transcriber-backend.onrender.com`

### 4️⃣ **Deploy Frontend Service**

**Create Web Service for Frontend:**
1. Render Dashboard → New → Web Service
2. Configure:
   - **Name**: `multilingual-transcriber-frontend`
   - **Runtime**: Node 20
   - **Build Command**:
     ```bash
     cd frontend && npm install && npm run build
     ```
   - **Start Command**:
     ```bash
     cd frontend && npm start
     ```
   - **Plan**: Free tier OK for frontend

3. **Environment Variables**:
   - `NEXT_PUBLIC_API_URL`: `https://multilingual-transcriber-backend.onrender.com`
   - `NODE_ENV`: production
   - `NODE_VERSION`: 20

4. Click "Deploy"

**Get Frontend URL:**
- After deployment: `https://multilingual-transcriber-frontend.onrender.com`

### 5️⃣ **Optional: Deploy Ollama Service**

For LLM-powered answer generation (requires GPU):

1. Render Dashboard → New → Web Service
2. Configure:
   - **Name**: `multilingual-transcriber-ollama`
   - **Runtime**: Docker
   - **Build Command**: `docker build -f ollama.Dockerfile -t ollama .`
   - **Start Command**: `ollama serve`
   - **Plan**: Pro (GPU required)

3. **Environment Variables**:
   - `OLLAMA_HOST`: 0.0.0.0:11434

4. Click "Deploy"

**Get Ollama URL:**
- After deployment: `https://multilingual-transcriber-ollama.onrender.com:11434`

### 6️⃣ **Update Backend for Remote Ollama** (if deploying Ollama separately)

Update `backend/api.py`:
```python
from backend.rag import OllamaGenerator, SimpleContextGenerator, get_default_generator

# For remote Ollama:
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
rag_generator = OllamaGenerator(base_url=OLLAMA_HOST)
```

Then redeploy backend service.

---

## 🐳 Using Docker Locally Before Deploying

Test deployment locally with Docker:

### Start Everything Locally

```bash
# Build and start all services
docker-compose up --build

# Ollama pulls model (requires separate command)
docker exec <container-id> ollama pull mistral
```

### Access Services

- **Backend**: http://localhost:8000
- **Frontend**: http://localhost:3000
- **Ollama**: http://localhost:11434 (if running)

### Stop Services

```bash
docker-compose down
```

---

## 🔐 Environment Variables for Production

Add these to Render environment:

```bash
# Backend
LOG_LEVEL=INFO
OLLAMA_HOST=http://ollama-service:11434  # or leave blank for fallback
PYTHONUNBUFFERED=1

# Frontend
NEXT_PUBLIC_API_URL=https://multilingual-transcriber-backend.onrender.com
NODE_ENV=production
```

---

## 📊 Render Pricing

| Service | Plan | Cost | Notes |
|---------|------|------|-------|
| Backend (FastAPI) | Free | $0 | Spins down after 15min inactivity |
| Backend | Starter | $7/mo | Always running |
| Frontend (Next.js) | Free | $0 | Spins down after inactivity |
| Frontend | Starter | $7/mo | Always running |
| Ollama (if GPU) | Pro | $24+/mo | GPU required |
| **Total** | **Free** | **$0** | Works but with limitations |
| **Total** | **Production** | **$38+/mo** | Recommended for business use |

---

## 🚀 Deployment Workflow

### Automatic Deployment

Once connected to GitHub, Render automatically deploys when you:
```bash
git push origin master
```

### Manual Deployment

In Render Dashboard:
1. Select Service
2. Click "Manual Deploy"
3. Choose "Deploy latest commit"

---

## ✅ Post-Deployment Checks

### 1. **Backend Health**
```bash
curl https://multilingual-transcriber-backend.onrender.com/health
# Should return: {"status": "healthy", "device": "cpu", ...}
```

### 2. **Frontend Access**
```bash
curl https://multilingual-transcriber-frontend.onrender.com
# Should return HTML (Next.js app)
```

### 3. **Query RAG System**
```bash
curl -X POST https://multilingual-transcriber-backend.onrender.com/rag/query \
  -H "Content-Type: application/json" \
  -d '{"question": "Test", "use_llm": false}'
```

### 4. **Check Logs**
In Render Dashboard:
1. Select Service
2. Click "Logs"
3. Watch real-time logs for errors

---

## 🐛 Troubleshooting

### Build Fails

**Error**: `ModuleNotFoundError: No module named 'backend'`

**Solution**: Ensure `backend/__init__.py` exists in repo:
```bash
touch backend/__init__.py
git add backend/__init__.py
git commit -m "Add backend __init__.py"
git push
```

### Frontend Can't Connect to Backend

**Error**: CORS errors or 404

**Solution**: Check `NEXT_PUBLIC_API_URL` is correctly set:
```bash
# In Render → Frontend Service → Environment
NEXT_PUBLIC_API_URL=https://multilingual-transcriber-backend.onrender.com
```

### Ollama Connection Refused

**Expected**: Ollama not running on free tier

**Solution**: Set fallback generator in backend (already done):
```python
rag_generator = get_default_generator(prefer_ollama=True)
# Automatically falls back to SimpleContextGenerator if Ollama unavailable
```

### Service Spinning Down

**Free tier**: Services spin down after 15 min inactivity

**Solution**: Upgrade to Starter ($7/mo) for always-on

---

## 🔧 Advanced Configuration

### Using PostgreSQL

For persistent data storage:

1. In Render → New → PostgreSQL
2. Get connection string
3. Add to backend environment:
   ```bash
   DATABASE_URL=postgresql://user:password@host:5432/db
   ```
4. Update `backend/api.py` to use SQLAlchemy

### Custom Domain

1. Buy domain (GoDaddy, Namecheap, etc.)
2. In Render Service → Settings → Custom Domains
3. Add your domain
4. Update DNS records per Render instructions

### SSL Certificate

Render auto-generates free SSL certificates for all deployments ✅

---

## 📈 Monitoring & Logs

### View Logs

```bash
# In Render Dashboard
Service → Logs → Real-time streaming
```

### Set Up Alerts

1. Render → Settings → Notifications
2. Enable email alerts for deployment failures

### Performance Metrics

1. Service → Metrics
2. Monitor CPU, memory, network usage

---

## 🔄 CI/CD with GitHub Actions

Optional: Add automated testing before deployment

Create `.github/workflows/test.yml`:
```yaml
name: Test & Deploy

on:
  push:
    branches: [master]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: 3.11
      - run: pip install -r requirements.txt -r backend/requirements.txt
      - run: python RAG_VALIDATION.py
```

Then push and Render auto-deploys after tests pass.

---

## 🎓 What You've Deployed

✅ **Production-Ready RAG System** with:
- FastAPI backend with Whisper ASR
- Next.js frontend with real-time UI
- Ollama integration for LLM generation
- Graceful fallback if Ollama unavailable
- Multi-language support (100+ languages)
- Speaker diarization
- Auto-transcript indexing
- Citation tracking & hallucination detection

✅ **Monitoring & Logging**
✅ **Auto-scaling** (on paid plans)
✅ **SSL/HTTPS** automatic
✅ **CI/CD Ready** with GitHub

---

## 📱 Access Your Deployment

After successful deployment:

1. **Web App**: https://multilingual-transcriber-frontend.onrender.com
2. **API Docs**: https://multilingual-transcriber-backend.onrender.com/docs
3. **Health Check**: https://multilingual-transcriber-backend.onrender.com/health

---

## 🆘 Getting Help

- **Render Docs**: https://render.com/docs
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **Next.js Docs**: https://nextjs.org/docs
- **Project Issues**: Check GitHub Issues

---

## ✨ Summary

| Step | Time | Status |
|------|------|--------|
| Create Render account | 5 min | ✅ |
| Deploy backend | 10 min | ✅ |
| Deploy frontend | 10 min | ✅ |
| Test endpoints | 5 min | ✅ |
| **Total** | **30 min** | ✅ |

**Your AI internship-ready system is now live on the internet! 🎉**
