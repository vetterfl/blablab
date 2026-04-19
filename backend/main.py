from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from limiter import limiter
from database import engine, Base
from routers import transcribe, refine
from routers import auth as auth_router
from routers import presets as presets_router
from routers import settings as settings_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="BlabLab")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(auth_router.router, prefix="/api")
app.include_router(transcribe.router, prefix="/api")
app.include_router(refine.router, prefix="/api")
app.include_router(presets_router.router, prefix="/api")
app.include_router(settings_router.router, prefix="/api")


# Serve frontend — registered last so API routes take priority
frontend_path = Path(__file__).parent.parent / "frontend"
app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="frontend")
