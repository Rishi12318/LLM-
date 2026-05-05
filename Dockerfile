# Multi-stage build for a single-service deployment that serves the frontend and API together

FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend

COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ ./
ENV NEXT_TELEMETRY_DISABLED=1 \
    NEXT_PUBLIC_API_URL=/api
RUN npm run build

FROM python:3.11-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt* ./
COPY backend/ ./backend/
COPY models/ ./models/
COPY pipeline/ ./pipeline/
COPY utils/ ./utils/

RUN pip install --user --no-cache-dir -r requirements.txt
RUN if [ -f backend/requirements.txt ]; then pip install --user --no-cache-dir -r backend/requirements.txt; fi

FROM python:3.11-slim AS runtime

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /root/.local /root/.local
COPY . .
COPY --from=frontend-builder /app/frontend/out ./frontend/out

ENV PATH=/root/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    LOG_LEVEL=INFO \
    FRONTEND_DIST_DIR=/app/frontend/out

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

CMD ["python", "-m", "uvicorn", "backend.api:app", "--host", "0.0.0.0", "--port", "8000"]
