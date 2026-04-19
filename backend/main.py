import logging
import time
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
from limiter import limiter
from database import engine, Base
from routers import transcribe, refine
from routers import auth as auth_router
from routers import presets as presets_router
from routers import settings as settings_router

logger = logging.getLogger("blablab.access")

Base.metadata.create_all(bind=engine)

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


# Serve frontend — registered last so API routes take priority
# Use Vite build output if available, otherwise fall back to vanilla frontend
frontend_dist = Path(__file__).parent.parent / "frontend-dist"
frontend_legacy = Path(__file__).parent.parent / "frontend"
frontend_path = frontend_dist if frontend_dist.is_dir() else frontend_legacy
app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="frontend")
