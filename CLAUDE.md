# BlabLab

Self-hosted voice dictation app: record → transcribe (OpenRouter audio model) → refine (OpenRouter LLM).

## Commands

```bash
# Development — backend + frontend dev servers
cd backend && uvicorn main:app --reload          # API on :8000
cd frontend-vue && npm run dev                   # Vite on :5173 (proxies /api → :8000)

# Development with Docker (hot-reload)
docker compose -f docker-compose.yaml -f docker-compose.dev.yml up

# Production
docker compose -f docker-compose.yaml up -d --build

# Build frontend (outputs to frontend-dist/)
cd frontend-vue && npm run build

# Add a user (seeds default presets automatically)
cd backend && python add_user.py <username> <password>

# Add a user (Docker, container must be running)
docker compose exec app python add_user.py <username> <password>

# Migrate from legacy users.json + presets.yaml to SQLite
cd backend && python migrate.py
```

## Architecture

```
backend/           FastAPI app (Python 3.11)
  main.py          App entry; serves frontend-dist as static files
  database.py      SQLAlchemy engine, SessionLocal, Base, get_db (SQLite + WAL)
  models.py        User + Preset ORM models
  auth.py          JWT logic, bcrypt, get_current_user dependency
  config.py        Pydantic BaseSettings, AVAILABLE_MODELS list
  limiter.py       slowapi Limiter instance (separate to avoid circular import)
  routers/
    auth.py        POST /api/auth/login
    transcribe.py  POST /api/transcribe
    refine.py      POST /api/refine
    presets.py     CRUD /api/presets
    settings.py    GET/PUT /api/settings, POST /api/settings/change-password
  services/
    transcribe.py  OpenRouter /v1/audio/transcriptions (Whisper-style multipart) for STT
    llm.py         OpenRouter LLM refinement
    users.py       User CRUD + default preset seeding
    presets.py     Preset CRUD
  add_user.py      CLI to add users to SQLite DB
  migrate.py       One-shot migration from JSON/YAML to SQLite
frontend-vue/      Vue 3 + Vite + Pinia SPA
  src/
    stores/        auth.js, presets.js, settings.js (Pinia)
    components/    AppHeader, LoginOverlay, RecordSection, etc.
    api/client.js  authFetch wrapper + typed API helpers
frontend/          Legacy vanilla JS frontend (fallback)
frontend-dist/     Vite build output (gitignored, built in Docker)
```

## Environment

Required in `.env` (copy from `.env.example`):
- `OPENROUTER_API_KEY`
- `SECRET_KEY` — generate with `python -c "import secrets; print(secrets.token_hex(32))"`
- `OPENROUTER_MODEL` (optional, default: `openai/gpt-4o-mini`) — refinement LLM
- `TRANSCRIPTION_MODEL` (optional, default: `openai/whisper-large-v3`) — ASR model via OpenRouter `/v1/audio/transcriptions`
- `DATABASE_URL` (optional, default: `sqlite:///./blablab.db`)

Refinement model list: `backend/models.yaml`. Transcription model list: `backend/transcription_models.yaml`.

## Gotchas

- Users are stored in SQLite (`blablab.db`). Create with `add_user.py` which also seeds default presets.
- All `/api/*` routes require a valid JWT (`Depends(get_current_user)`). The only public endpoint is `POST /api/auth/login`.
- Model resolution order: `preset.model → user.default_model → settings.openrouter_model`.
- `limiter.py` exists as a separate module purely to avoid a circular import between `main.py` and `routers/auth.py`.
- Vue frontend uses Pinia store watchers to auto-fetch presets on login — no manual reload needed.
- `main.py` serves `frontend-dist/` if it exists, otherwise falls back to `frontend/`.
- Audio upload size, recording duration, and refine transcript length are editable per-instance under Settings → Limits (admin-only). Defaults: 25 MB, 90 s, 2000 chars. Env overrides: `MAX_AUDIO_BYTES`, `MAX_RECORDING_SECONDS`, `MAX_TRANSCRIPT_CHARS` (only seed initial DB row).
