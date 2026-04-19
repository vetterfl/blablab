# BlabLab

Self-hosted voice dictation app. Record speech in the browser, get an AI transcription, then refine it into a formal email, bullet points, short reply, or any custom preset — all in one click.

**Stack:** Python / FastAPI · OpenAI Whisper · OpenRouter LLM · Vanilla JS · Docker + nginx

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
   Users are stored in `backend/users.json` (gitignored). Run the script once per user.

3. **Run** (pick one):

   | Mode | Command |
   |------|---------|
   | Development (hot-reload) | `docker compose -f docker-compose.yml -f docker-compose.dev.yml up` |
   | Production | `docker compose up -d --build` |
   | No Docker | `cd backend && pip install -r requirements.txt && uvicorn main:app --reload` |

3. Open `http://localhost:8000` (dev) or your server's domain (prod).

---

## Usage

1. **Record** — click *Record*, speak, click *Stop*.
2. **Edit** — the transcript appears in a text box. Fix any mistakes before refining.
3. **Refine** — click a preset button to reformat the text with AI:
   - **Formal Email** — polished, professional email body
   - **Short Reply** — 1–3 sentence condensed reply
   - **Bullet Points** — key ideas as a dash list
   - **Casual Message** — friendly, conversational tone
   - **Clean Up** — grammar/punctuation fix, filler words removed
4. **Copy** — click *Copy to Clipboard* to grab the refined output.

---

## Customising presets

Edit `backend/presets.yaml` — add, remove, or reword any preset. No code changes needed, just restart the server.

```yaml
presets:
  - id: my_preset
    label: "My Preset"
    prompt: "Rewrite the following as ..."
```

To change the LLM model, update `OPENROUTER_MODEL` in `.env` to any model available on [openrouter.ai](https://openrouter.ai/models).

---

## Authentication

The app requires login. All API routes are protected — unauthenticated requests receive a `401`.

**How it works:**
- On first visit, a login overlay covers the UI
- After a successful login, a JWT is stored in `localStorage` (24-hour expiry)
- Clicking *Sign out* in the header clears the token and returns to the login screen
- An expired or invalid token automatically shows the login overlay again

**Managing users** (run from `backend/`):
```bash
python add_user.py <username> <password>   # add a user
```

With Docker (container must be running):
```bash
docker compose exec app python add_user.py <username> <password>
```

There is no delete command — remove an entry from `backend/users.json` manually to revoke access.

---

## Production deployment

The prod compose stack runs the FastAPI app behind an nginx reverse proxy.
Update `nginx/default.conf` with your domain, then add TLS:

```bash
sudo certbot --nginx -d your.domain.com
```

Mount the generated certs into the nginx container (see the commented block in `nginx/default.conf`).
