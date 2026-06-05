import time
import httpx

CATALOG_URL = "https://openrouter.ai/api/v1/models"
MODEL_ENDPOINTS_URL = "https://openrouter.ai/api/v1/models/{slug}/endpoints"
CACHE_TTL_SECONDS = 300  # 5 minutes

# OpenRouter's /v1/models listing excludes ASR models (output_modalities=transcription).
# Hardcode known ASR slugs so the autocomplete works. Admins can still add any slug
# that passes the per-endpoint probe.
KNOWN_TRANSCRIPTION_MODELS = [
    "openai/whisper-large-v3",
    "openai/whisper-1",
    "qwen/qwen3-asr-flash-2026-02-10",
]

_cache: list | None = None
_cache_at: float = 0.0


async def fetch_catalog(force: bool = False) -> list[dict]:
    global _cache, _cache_at
    now = time.time()
    if not force and _cache is not None and now - _cache_at < CACHE_TTL_SECONDS:
        return _cache

    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(CATALOG_URL)
    if response.status_code != 200:
        raise RuntimeError(
            f"OpenRouter catalog error {response.status_code}: {response.text}"
        )
    data = (response.json() or {}).get("data") or []
    _cache = data
    _cache_at = now
    return data


async def model_endpoints(slug: str) -> dict | None:
    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(MODEL_ENDPOINTS_URL.format(slug=slug))
    if response.status_code == 404:
        return None
    if response.status_code != 200:
        raise RuntimeError(
            f"OpenRouter model probe error {response.status_code}: {response.text}"
        )
    return (response.json() or {}).get("data")


def _output_modalities(entry: dict) -> list[str]:
    arch = entry.get("architecture") or {}
    mods = arch.get("output_modalities")
    return mods if isinstance(mods, list) else []


def _is_transcription(entry: dict) -> bool:
    return "transcription" in _output_modalities(entry)


async def catalog_slugs(kind: str | None = None) -> list[str]:
    if kind == "transcription":
        # /v1/models excludes ASR models. Use hardcoded list, verified live.
        verified = []
        for slug in KNOWN_TRANSCRIPTION_MODELS:
            try:
                if await model_endpoints(slug):
                    verified.append(slug)
            except RuntimeError:
                pass
        return verified

    data = await fetch_catalog()
    slugs = [e.get("id") for e in data if e.get("id")]
    return sorted(set(slugs))


async def slug_exists(slug: str, kind: str | None = None) -> bool:
    if kind == "transcription":
        info = await model_endpoints(slug)
        return bool(info) and _is_transcription(info)

    # refine: must appear in /v1/models listing
    return slug in await catalog_slugs(kind=None)
