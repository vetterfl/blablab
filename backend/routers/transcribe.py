from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from services.whisper import transcribe_audio
from auth import get_current_user

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

MAX_AUDIO_BYTES = 25 * 1024 * 1024  # 25 MB (Whisper API limit)


@router.post("/transcribe")
async def transcribe_endpoint(
    audio: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
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

    try:
        transcript = await transcribe_audio(
            audio_bytes, audio.filename or "audio.webm"
        )
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))

    return {"transcript": transcript}
