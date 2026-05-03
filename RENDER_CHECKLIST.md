# 📋 Render Deployment Checklist

## Pre-Deployment ✅

- [ ] GitHub account created and synced
- [ ] Code pushed to GitHub master branch
- [ ] All tests passing (`python RAG_VALIDATION.py`)
- [ ] Docker files created (Dockerfile, frontend.Dockerfile)
- [ ] Environment variables documented (.env.example)
- [ ] README updated with deployment info

## Render Setup ✅

- [ ] Render account created (https://render.com)
- [ ] GitHub repository connected to Render
- [ ] GitHub personal access token generated

## Backend Deployment ✅

- [ ] Create Backend Web Service
  - [ ] Name: `multilingual-transcriber-backend`
  - [ ] Runtime: Python 3.11
  - [ ] Build Command: `pip install -r requirements.txt && pip install -r backend/requirements.txt`
  - [ ] Start Command: `python -m uvicorn backend.api:app --host 0.0.0.0 --port $PORT`
  - [ ] Plan: Free (or Starter for always-on)
  
- [ ] Set Environment Variables:
  - [ ] `PYTHON_VERSION` = 3.11
  - [ ] `LOG_LEVEL` = INFO
  - [ ] `OLLAMA_HOST` = (leave blank for fallback or set to Ollama URL)

- [ ] Deploy and wait for success (~3-5 minutes)
- [ ] Test backend health: `curl https://<backend-url>/health`
- [ ] Note backend URL for frontend config

## Frontend Deployment ✅

- [ ] Create Frontend Web Service
  - [ ] Name: `multilingual-transcriber-frontend`
  - [ ] Runtime: Node 20
  - [ ] Build Command: `cd frontend && npm install && npm run build`
  - [ ] Start Command: `cd frontend && npm start`
  - [ ] Plan: Free tier OK

- [ ] Set Environment Variables:
  - [ ] `NEXT_PUBLIC_API_URL` = `https://<backend-url>`
  - [ ] `NODE_ENV` = production
  - [ ] `NODE_VERSION` = 20

- [ ] Deploy and wait for success (~5-10 minutes)
- [ ] Test frontend: Visit `https://<frontend-url>`

## Post-Deployment ✅

- [ ] Verify backend endpoint: `/health`
  ```bash
  curl https://<backend-url>/health
  # Expected: {"status": "healthy", ...}
  ```

- [ ] Verify frontend loads: `https://<frontend-url>`

- [ ] Test RAG query endpoint:
  ```bash
  curl -X POST https://<backend-url>/rag/query \
    -H "Content-Type: application/json" \
    -d '{"question": "Test", "use_llm": false}'
  ```

- [ ] Check logs in Render dashboard for errors

- [ ] Test file upload (if applicable)

- [ ] Verify frontend → backend communication (check browser console)

## Production Optimization ✅

- [ ] Upgrade backend to Starter plan ($7/mo) for always-on
- [ ] Upgrade frontend to Starter plan ($7/mo) if needed
- [ ] Set up custom domain (optional)
- [ ] Enable Render notifications for deployment alerts
- [ ] Set up monitoring/logging (optional)
- [ ] Review performance metrics in Render dashboard

## Optional: Ollama Deployment ✅

If LLM generation needed:

- [ ] Create Ollama Web Service (GPU required - Pro plan)
- [ ] Set environment variables
- [ ] Update backend `OLLAMA_HOST` to remote URL
- [ ] Pull model: `docker exec <container> ollama pull mistral`
- [ ] Redeploy backend with new OLLAMA_HOST

## Troubleshooting ✅

- [ ] Check "Logs" tab if services not running
- [ ] Verify environment variables are correct
- [ ] Ensure build commands don't have typos
- [ ] Check GitHub connection status
- [ ] Verify firewall/network rules if API calls fail

## Successful Deployment URLs

**Backend**: `https://multilingual-transcriber-backend.onrender.com`
- Health: `https://multilingual-transcriber-backend.onrender.com/health`
- API Docs: `https://multilingual-transcriber-backend.onrender.com/docs`

**Frontend**: `https://multilingual-transcriber-frontend.onrender.com`

---

## Quick Reference

### Useful Commands

```bash
# Check deployment status
git log --oneline -5

# Local Docker test before deploying
docker-compose up --build

# SSH into Render service (if available)
render ssh <service-id>

# View live logs
# Via Render Dashboard: Service → Logs
```

### Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: backend` | Run `touch backend/__init__.py && git add backend/__init__.py` |
| Frontend can't reach backend | Check `NEXT_PUBLIC_API_URL` env var |
| Service won't start | Check "Logs" for error messages |
| Slow cold starts | Upgrade to paid plan |
| Ollama connection refused | It's expected if not deployed; system uses fallback |

---

**Status**: Ready for deployment! 🚀
