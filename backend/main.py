from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routers import transcribe, refine
from config import load_presets

app = FastAPI(title="Dictator")

app.include_router(transcribe.router, prefix="/api")
app.include_router(refine.router, prefix="/api")


@app.get("/api/presets")
async def get_presets():
    presets = [{"id": p["id"], "label": p["label"]} for p in load_presets()]
    return {"presets": presets}


# Serve frontend — registered last so API routes take priority
frontend_path = Path(__file__).parent.parent / "frontend"
app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="frontend")
