from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File
from sqlalchemy.orm import Session

from auth import get_current_user
from database import get_db
from limiter import limiter
from services.app_settings import get_app_settings
from services.transcribe import transcribe_audio

router = APIRouter()

ALLOWED_AUDIO_PREFIXES = (
    "audio/webm",
    "audio/ogg",
    "audio/mp4",
    "audio/wav",
    "audio/mpeg",
    "audio/x-m4a",
    "audio/m4a",
    "application/octet-stream",
)



@router.post("/transcribe")
@limiter.limit("20/minute")
async def transcribe_endpoint(
    request: Request,
    audio: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    content_type = audio.content_type or ""
    if not any(content_type.startswith(p) for p in ALLOWED_AUDIO_PREFIXES):
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported audio format: {content_type}",
        )

    audio_bytes = await audio.read()
    app_settings = get_app_settings(db)

    if len(audio_bytes) > app_settings.max_audio_bytes:
        mb = app_settings.max_audio_bytes // (1024 * 1024)
        raise HTTPException(
            status_code=413, detail=f"Audio file too large (max {mb} MB)"
        )

    if len(audio_bytes) == 0:
        raise HTTPException(status_code=400, detail="Audio file is empty")

    try:
        result = await transcribe_audio(
            audio_bytes,
            audio.filename or "audio.webm",
            content_type=content_type,
            model=app_settings.transcription_model,
        )
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))

    return {
        "transcript": result["text"],
        "cost_usd": result.get("cost_usd"),
        "audio_bytes": len(audio_bytes),
    }
