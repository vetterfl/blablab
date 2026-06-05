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

MAX_AUDIO_BYTES = 25 * 1024 * 1024  # 25 MB


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

    if len(audio_bytes) > MAX_AUDIO_BYTES:
        raise HTTPException(
            status_code=413, detail="Audio file too large (max 25 MB)"
        )

    if len(audio_bytes) == 0:
        raise HTTPException(status_code=400, detail="Audio file is empty")

    app_settings = get_app_settings(db)

    try:
        transcript = await transcribe_audio(
            audio_bytes,
            audio.filename or "audio.webm",
            content_type=content_type,
            model=app_settings.transcription_model,
        )
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))

    return {"transcript": transcript}
