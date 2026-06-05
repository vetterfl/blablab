import logging
import time
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from sqlalchemy import text
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
from limiter import limiter
from database import engine, Base
from routers import transcribe, refine
from routers import auth as auth_router
from routers import presets as presets_router
from routers import settings as settings_router
from routers import users as users_router
from routers import admin_models as admin_models_router

logger = logging.getLogger("uvicorn.error")

Base.metadata.create_all(bind=engine)

# Inline migration: add is_admin column if it doesn't exist yet
with engine.connect() as conn:
    cols = [row[1] for row in conn.execute(text("PRAGMA table_info(users)"))]
    if "is_admin" not in cols:
        conn.execute(text("ALTER TABLE users ADD COLUMN is_admin BOOLEAN NOT NULL DEFAULT 0"))
        conn.commit()

    cols = [row[1] for row in conn.execute(text("PRAGMA table_info(app_settings)"))]
    if cols:
        if "max_audio_bytes" not in cols:
            conn.execute(text(f"ALTER TABLE app_settings ADD COLUMN max_audio_bytes INTEGER NOT NULL DEFAULT {25 * 1024 * 1024}"))
        if "max_recording_seconds" not in cols:
            conn.execute(text("ALTER TABLE app_settings ADD COLUMN max_recording_seconds INTEGER NOT NULL DEFAULT 90"))
        if "max_transcript_chars" not in cols:
            conn.execute(text("ALTER TABLE app_settings ADD COLUMN max_transcript_chars INTEGER NOT NULL DEFAULT 2000"))
        conn.commit()

# Migrate legacy chat-completion STT entries → ASR-only model list, then merge YAML.
from database import SessionLocal
from models import AvailableModel, AppSettings
from services.available_models import seed_from_yaml

LEGACY_STT_CHAT_SLUGS = {
    "google/gemini-flash-latest",
    "google/gemini-pro-latest",
    "google/gemini-2.5-flash",
    "google/gemini-2.5-flash-lite",
    "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",
    "xiaomi/mimo-v2.5",
}

with SessionLocal() as _db:
    _db.query(AvailableModel).filter(
        AvailableModel.kind == "transcription",
        AvailableModel.slug.in_(LEGACY_STT_CHAT_SLUGS),
    ).delete(synchronize_session=False)
    _db.commit()

    row = _db.query(AppSettings).filter(AppSettings.id == 1).first()
    if row is not None and row.transcription_model in LEGACY_STT_CHAT_SLUGS:
        row.transcription_model = "openai/whisper-large-v3"
        _db.commit()

    seed_from_yaml(_db)

app = FastAPI(title="BlabLab")

# Trust X-Forwarded-For / X-Real-IP from the reverse proxy
app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*")

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.middleware("http")
async def access_log(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    ms = (time.perf_counter() - start) * 1000
    ip = request.client.host if request.client else "-"
    logger.info(
        '%s "%s %s" %s %.0fms',
        ip,
        request.method,
        request.url.path,
        response.status_code,
        ms,
    )
    return response

app.include_router(auth_router.router, prefix="/api")
app.include_router(transcribe.router, prefix="/api")
app.include_router(refine.router, prefix="/api")
app.include_router(presets_router.router, prefix="/api")
app.include_router(settings_router.router, prefix="/api")
app.include_router(users_router.router, prefix="/api")
app.include_router(admin_models_router.router, prefix="/api")


# Serve frontend — registered last so API routes take priority
# Use Vite build output if available, otherwise fall back to vanilla frontend
frontend_dist = Path(__file__).parent.parent / "frontend-dist"
frontend_legacy = Path(__file__).parent.parent / "frontend"
frontend_path = frontend_dist if frontend_dist.is_dir() else frontend_legacy
app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="frontend")
