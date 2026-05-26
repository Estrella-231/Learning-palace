import json
import os
import re
from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Load .env first so ${VAR} placeholders in config.json get resolved
load_dotenv(Path(__file__).parent.parent.parent / ".env")

CONFIG_PATH = Path(__file__).parent.parent.parent / "config.json"


def _load_config() -> dict:
    if not CONFIG_PATH.exists():
        return {}
    raw = CONFIG_PATH.read_text()
    # Expand ${ENV_VAR} placeholders
    def replace_env(m):
        return os.environ.get(m.group(1), "")
    raw = re.sub(r"\$\{(\w+)\}", replace_env, raw)
    return json.loads(raw)


_config = _load_config()


class Settings(BaseSettings):
    database_url: str = _config.get(
        "database_url",
        "postgresql+asyncpg://postgres:postgres@localhost:5432/learning_palace",
    )
    database_sync_url: str = _config.get(
        "database_sync_url",
        "postgresql://postgres:postgres@localhost:5432/learning_palace",
    )

    # Model configs
    @property
    def models(self) -> dict:
        return _config.get("models", {})

    @property
    def default_model_name(self) -> str:
        return self.models.get("default", "claude")

    @property
    def extraction_config(self) -> dict:
        return _config.get("extraction", {"model": "default", "temperature": 0.3})

    @property
    def embedding_config(self) -> dict:
        return _config.get("embedding", {})

    class Config:
        env_file = ".env"


settings = Settings()
