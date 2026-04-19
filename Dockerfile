# ── Stage 1: build frontend ────────────────────────────────────────────────────
FROM node:22-alpine AS node-builder

WORKDIR /build
COPY frontend-vue/package*.json ./
RUN npm ci
COPY frontend-vue/ .
RUN npm run build


# ── Stage 2: build Python dependencies ────────────────────────────────────────
FROM python:3.11-slim AS py-builder

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .
RUN python -m venv /venv && \
    /venv/bin/pip install --upgrade pip && \
    /venv/bin/pip install --no-cache-dir -r requirements.txt


# ── Stage 3: final image ──────────────────────────────────────────────────────
FROM python:3.11-slim AS final

WORKDIR /app

# Copy venv from builder
COPY --from=py-builder /venv /venv

# Copy application code
COPY backend/ ./backend/
COPY --from=node-builder /frontend-dist ./frontend-dist/

WORKDIR /app/backend

ENV PATH="/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--no-access-log"]
