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

def load_models() -> list[str]:
    models_path = Path(__file__).parent / "models.yaml"
    if not models_path.exists():
        return ["openai/gpt-4o-mini"]
    with open(models_path) as f:
        data = yaml.safe_load(f)
    return data["models"]


AVAILABLE_MODELS = load_models()


def load_presets() -> list[dict]:
    presets_path = Path(__file__).parent / "presets.yaml"
    with open(presets_path) as f:
        data = yaml.safe_load(f)
    return data["presets"]
