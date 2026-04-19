# BlabLab

Self-hosted voice dictation app. Record speech in the browser, get an AI transcription, then refine it into a formal email, bullet points, short reply, or any custom preset — all in one click.

**Stack:** Python / FastAPI · SQLite + SQLAlchemy · Vue 3 + Vite + Pinia · OpenAI Whisper · OpenRouter LLM · Docker

---

## Setup

1. **Copy and fill in your API keys:**
   ```bash
   cp .env.example .env
   ```
   ```env
   OPENAI_API_KEY=sk-...
   OPENROUTER_API_KEY=sk-or-...
   OPENROUTER_MODEL=openai/gpt-4o-mini   # any OpenRouter model slug
   SECRET_KEY=                            # generate with: python -c "import secrets; print(secrets.token_hex(32))"
   ```

2. **Add at least one user:**
   ```bash
   cd backend && pip install -r requirements.txt
   python add_user.py <username> <password>
   ```
   Users are stored in SQLite (`blablab.db`). Each new user is seeded with default presets.

3. **Run** (pick one):

   | Mode | Command |
   |------|---------|
   | Development (no Docker) | `cd backend && uvicorn main:app --reload` + `cd frontend-vue && npm run dev` |
   | Development (Docker) | `docker compose -f docker-compose.yml -f docker-compose.dev.yml up` |
   | Production | `docker compose up -d --build` |

4. Open `http://localhost:5173` (Vite dev) or `http://localhost:8000` (Docker / uvicorn).

---

## Usage

1. **Record** — click the mic button, speak, click Stop.
2. **Edit** — the transcript appears in a text box. Fix any mistakes.
3. **Refine** — pick a preset in the right panel to reformat with AI:
   - **Formal Email** — polished, professional email body
   - **Short Reply** — 1–3 sentence condensed reply
   - **Bullet Points** — key ideas as a dash list
   - **Casual Message** — friendly, conversational tone
   - **Clean Up** — grammar/punctuation fix, filler words removed
4. **Copy** — grab the refined output.

---

## Per-user presets

Each user has their own set of presets stored in the database. New users are seeded with the defaults from `backend/presets.yaml`.

Presets can be managed via the API:
- `GET /api/presets` — list presets
- `POST /api/presets` — create a preset
- `PUT /api/presets/{slug}` — update a preset
- `DELETE /api/presets/{slug}` — delete a preset

Each preset can optionally override the LLM model. The resolution order is: preset model → user default model → global `OPENROUTER_MODEL`.

---

## Settings

- `GET /api/settings` — get user settings and available models
- `PUT /api/settings` — update default model
- `POST /api/settings/change-password` — change password

---

## Authentication

The app requires login. All API routes are protected — unauthenticated requests receive a `401`.

- On first visit, a login overlay covers the UI
- After a successful login, a JWT is stored in `localStorage` (24-hour expiry)
- Clicking *Sign out* clears the token and returns to the login screen

**Managing users:**
```bash
# Local
cd backend && python add_user.py <username> <password>

# Docker (container must be running)
docker compose exec app python add_user.py <username> <password>
```

Registration is admin-only — there is no self-signup.

---

## Migrating from legacy format

If upgrading from the file-based version (users.json + presets.yaml):

```bash
cd backend && python migrate.py
```

This is idempotent — safe to run multiple times.

---

## Production deployment

The Docker image builds the Vue frontend and serves it via FastAPI. Place a reverse proxy (Caddy, nginx, etc.) in front for TLS:

```
your.domain.com → localhost:8000
```

Data is stored in a Docker named volume (`blablab_data`) mounted at `/app/backend/data`.
