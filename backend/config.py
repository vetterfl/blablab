from pathlib import Path
from pydantic_settings import BaseSettings
import yaml


class Settings(BaseSettings):
    openai_api_key: str
    openrouter_api_key: str
    openrouter_model: str = "openai/gpt-4o-mini"
    host: str = "127.0.0.1"
    port: int = 8000
    secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24  # 24 hours

    database_url: str = "sqlite:///./blablab.db"

    class Config:
        env_file = Path(__file__).parent.parent / ".env"


settings = Settings()

AVAILABLE_MODELS = [
    "openai/gpt-4o-mini",
    "openai/gpt-4o",
    "anthropic/claude-sonnet-4-5-20250514",
    "anthropic/claude-3-5-haiku-20241022",
    "google/gemini-2.0-flash-001",
    "meta-llama/llama-3.1-8b-instruct",
]


def load_presets() -> list[dict]:
    presets_path = Path(__file__).parent / "presets.yaml"
    with open(presets_path) as f:
        data = yaml.safe_load(f)
    return data["presets"]
