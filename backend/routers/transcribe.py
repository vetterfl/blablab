from fastapi import APIRouter, HTTPException, UploadFile, File
from services.whisper import transcribe_audio

router = APIRouter()

ALLOWED_CONTENT_TYPES = {
    "audio/webm",
    "audio/ogg",
    "audio/mp4",
    "audio/wav",
    "audio/mpeg",
    "audio/x-m4a",
    "audio/m4a",
    "application/octet-stream",  # Some browsers send this for webm
}

MAX_AUDIO_BYTES = 25 * 1024 * 1024  # 25 MB (Whisper API limit)


@router.post("/transcribe")
async def transcribe_endpoint(audio: UploadFile = File(...)):
    if audio.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported audio format: {audio.content_type}",
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
