import httpx
from config import settings

WHISPER_URL = "https://api.openai.com/v1/audio/transcriptions"


async def transcribe_audio(audio_bytes: bytes, filename: str) -> str:
    headers = {"Authorization": f"Bearer {settings.openai_api_key}"}
    files = {"file": (filename, audio_bytes, "audio/webm")}
    data = {"model": "whisper-1", "response_format": "text"}

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            WHISPER_URL, headers=headers, files=files, data=data
        )

    if response.status_code != 200:
        raise RuntimeError(
            f"Whisper API error {response.status_code}: {response.text}"
        )

    return response.text.strip()
