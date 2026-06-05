import base64
import httpx
from config import settings

OPENROUTER_URL = "https://openrouter.ai/api/v1/audio/transcriptions"

FORMAT_MAP = {
    "audio/webm": "webm",
    "audio/ogg": "ogg",
    "audio/mp4": "mp4",
    "audio/wav": "wav",
    "audio/x-wav": "wav",
    "audio/mpeg": "mp3",
    "audio/mp3": "mp3",
    "audio/x-m4a": "m4a",
    "audio/m4a": "m4a",
    "audio/flac": "flac",
}


def detect_format(content_type: str, filename: str) -> str:
    ct = (content_type or "").split(";")[0].strip().lower()
    if ct in FORMAT_MAP:
        return FORMAT_MAP[ct]
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext in {"webm", "ogg", "mp4", "wav", "mp3", "m4a", "flac"}:
        return ext
    return "webm"


async def transcribe_audio(
    audio_bytes: bytes,
    filename: str,
    content_type: str = "",
    model: str | None = None,
) -> dict:
    audio_format = detect_format(content_type, filename)
    audio_b64 = base64.b64encode(audio_bytes).decode("ascii")
    resolved_model = model or settings.transcription_model

    headers = {
        "Authorization": f"Bearer {settings.openrouter_api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost",
        "X-Title": "BlabLab",
    }
    payload = {
        "input_audio": {
            "data": audio_b64,
            "format": audio_format,
        },
        "model": resolved_model,
    }

    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(OPENROUTER_URL, headers=headers, json=payload)

    if response.status_code != 200:
        raise RuntimeError(
            f"OpenRouter transcription error {response.status_code}: {response.text}"
        )

    data = response.json()
    text = data.get("text")
    if not text:
        raise RuntimeError(f"OpenRouter transcription returned no text: {data}")
    usage = data.get("usage") or {}
    return {"text": text.strip(), "cost_usd": usage.get("cost")}
