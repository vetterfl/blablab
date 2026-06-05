import httpx
from config import settings

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


async def refine_text(
    transcript: str, system_prompt: str, model: str | None = None
) -> dict:
    headers = {
        "Authorization": f"Bearer {settings.openrouter_api_key}",
        "HTTP-Referer": "http://localhost",
        "X-Title": "BlabLab",
    }
    resolved_model = model or settings.openrouter_model
    payload = {
        "model": resolved_model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": transcript},
        ],
        "temperature": 0.4,
        "max_tokens": 1024,
        "usage": {"include": True},
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(OPENROUTER_URL, headers=headers, json=payload)

    if response.status_code != 200:
        raise RuntimeError(
            f"OpenRouter API error {response.status_code}: {response.text}"
        )

    data = response.json()
    content = data["choices"][0]["message"]["content"].strip()
    usage = data.get("usage") or {}
    cost_usd = usage.get("cost")
    return {"content": content, "cost_usd": cost_usd}
