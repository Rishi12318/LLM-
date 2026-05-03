# Multi-stage build for Next.js frontend

# Stage 1: Dependencies
FROM node:20-alpine AS deps

WORKDIR /app

COPY frontend/package*.json ./

RUN npm ci --only=production && \
    npm ci --only=development

# Stage 2: Build
FROM node:20-alpine AS builder

WORKDIR /app

COPY frontend/package*.json ./
COPY --from=deps /app/node_modules ./node_modules
COPY frontend/ . 

ENV NEXT_TELEMETRY_DISABLED=1

RUN npm run build

# Stage 3: Runtime
FROM node:20-alpine AS runtime

WORKDIR /app

ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1 \
    NEXT_PUBLIC_API_URL=http://localhost:8000

COPY frontend/package*.json ./
COPY --from=deps /app/node_modules ./node_modules
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public

RUN apk add --no-cache curl

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:3000 || exit 1

CMD ["npm", "start"]
