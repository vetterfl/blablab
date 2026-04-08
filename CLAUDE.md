# BlabLab

Self-hosted voice dictation app: record → transcribe (Whisper) → refine (OpenRouter LLM).

## Commands

```bash
# Development (hot-reload, no nginx)
docker compose -f docker-compose.yml -f docker-compose.dev.yml up

# Production
docker compose up -d --build

# No Docker
cd backend && uvicorn main:app --reload

# Add a user
cd backend && python add_user.py <username> <password>

# Add a user (Docker, container must be running)
docker compose exec app python add_user.py <username> <password>
```

## Architecture

```
backend/        FastAPI app (Python 3.11)
  main.py       App entry point; also serves frontend as static files
  auth.py       JWT logic, bcrypt, get_current_user dependency
  limiter.py    slowapi Limiter instance (separate to avoid circular import)
  routers/      auth.py (login), transcribe.py, refine.py
  services/     whisper.py (OpenAI), llm.py (OpenRouter)
  add_user.py   CLI to add users to users.json
frontend/       Vanilla JS SPA — no build step, served by FastAPI
nginx/          Reverse proxy config (prod only; Caddy used in practice)
```

## Environment

Required in `.env` (copy from `.env.example`):
- `OPENAI_API_KEY`
- `OPENROUTER_API_KEY`
- `SECRET_KEY` — generate with `python -c "import secrets; print(secrets.token_hex(32))"`
- `OPENROUTER_MODEL` (optional, default: `openai/gpt-4o-mini`)

## Gotchas

- `users.json` is gitignored — must exist and have at least one user before the app is usable. Create it with `add_user.py`.
- All `/api/*` routes require a valid JWT (`Depends(get_current_user)`). The only public endpoint is `POST /api/auth/login`.
- `limiter.py` exists as a separate module purely to avoid a circular import between `main.py` and `routers/auth.py`.
- Frontend JS calls `authFetch()` (defined in `auth.js`) instead of `fetch()` — it injects the Bearer token and handles 401s globally.
- Max transcript length for `/api/refine` is 2000 characters. Max recording duration is 90 seconds (frontend enforced).
